#!/usr/bin/env python3
"""
NasipQuest Economy Simulation

Senaryo:
- 10,000 kullanıcı
- 30 gün
- Her kullanıcı günde 0–3 arası görev yapabilir
- RewardEngine + Treasury + NCR fiyatını kabaca simüle eder

Amaç:
- Günlük NCR mint
- Treasury dayanıklılığı
- NCR fiyat eğrisi
- Kullanıcı başı ortalama kazanç

Bu standalone bir simülasyon.
NovaCore'a entegre etmek için:
- compute_final_ncr yerine gerçek RewardEngine fonksiyonunu
- fiyat güncelleme yerine pricing.py fonksiyonunu
koyabilirsin.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict
from statistics import mean

# -----------------------------
# CONFIG
# -----------------------------

N_USERS = 10_000
N_DAYS = 30

# Başlangıç Treasury (fiat / USDT cinsinden)
INITIAL_TREASURY_RESERVES = 500_000.0  # örnek

# NCR başlangıç fiyatı (TRY cinsinden)
INITIAL_NCR_PRICE = 1.0

# Günlük redemption oranı (basılan NCR'ın yüzde kaçı fiata çevriliyor?)
REDEMPTION_RATE = 0.10  # %10

# Günlük burn oranı (sistem içi sink mekanizmaları vs.)
BURN_RATE = 0.02  # %2

# Treasury hedef coverage ratio
TARGET_COVERAGE = 1.2  # %120 teminat

# Fiyat ayar duyarlılığı
K_COVERAGE = 0.4
K_FLOW = 0.2
SMOOTHING_ALPHA = 0.3
MAX_DAILY_PRICE_CHANGE = 0.15  # %15

# Treasury Cap
TREASURY_DAILY_LIMIT = 200_000.0
TREASURY_DAMPING_TABLE = {
    0.70: 1.00,
    0.85: 0.80,
    0.95: 0.60,
    1.00: 0.30,
    1.10: 0.10,
}

# -----------------------------
# USER MODEL
# -----------------------------


@dataclass
class UserState:
    level: int
    streak: int
    siyah_score: float
    risk_score: float
    balance_ncr: float = 0.0

    def update_after_day(self, did_any_task: bool):
        # Streak mantığı: bugün görev yaptıysa +1, yoksa reset
        if did_any_task:
            self.streak += 1
        else:
            self.streak = 0

        # Basit evolution:
        # Kaliteli kullanıcıların siyah_score'u hafif yükselsin
        if self.siyah_score > 75 and did_any_task:
            self.siyah_score = min(100.0, self.siyah_score + random.uniform(0.0, 0.5))

        # RiskScore biraz mean-revert etsin
        if self.risk_score > 0:
            self.risk_score = max(0.0, self.risk_score - random.uniform(0.0, 0.2))


# -----------------------------
# ECONOMY STATE
# -----------------------------


@dataclass
class EconomyState:
    treasury_reserves_fiat: float
    ncr_outstanding: float
    ncr_price_try: float
    ema_coverage: float = 1.0
    ema_flow_index: float = 0.0
    daily_issued_ncr: float = 0.0  # Treasury cap için


@dataclass
class DayStats:
    day: int
    total_minted_ncr: float
    total_burned_ncr: float
    total_redeemed_ncr: float
    treasury_reserves_fiat: float
    ncr_outstanding: float
    ncr_price_try: float
    coverage_ratio: float
    treasury_load_ratio: float
    treasury_capped_ncr: float  # Treasury cap nedeniyle kesilen NCR


# -----------------------------
# HELPERS: REWARD FACTORS
# -----------------------------


def risk_penalty_from_score(risk_score: float) -> float:
    if risk_score <= 2:
        return 1.0
    elif risk_score <= 5:
        return 0.8
    elif risk_score <= 8:
        return 0.6
    else:
        return 0.0


def quality_mult_from_siyah_score(sq: float) -> float:
    if sq < 70:
        return 1.0
    elif sq >= 95:
        return 1.5
    else:
        # 70–95 arası linear artış: 1.0 → 1.5
        return 1.0 + (sq - 70.0) * 0.02  # biraz agresif versiyon


def compute_final_ncr_for_task(user: UserState, base_ncr: float) -> float:
    """
    Final NCR Formula v1:
    FinalNCR = (Base * LevelFactor * StreakFactor * RiskPenalty) * QualityMult * NasipFactor
    """
    if base_ncr <= 0:
        return 0.0

    level_factor = 1.0 + (user.level / 20.0)
    streak_factor = 1.0 + (user.streak * 0.04)
    rp = risk_penalty_from_score(user.risk_score)
    qm = quality_mult_from_siyah_score(user.siyah_score)
    nasip = random.uniform(0.85, 1.15)

    raw = base_ncr * level_factor * streak_factor * rp * qm * nasip
    return max(0.0, round(raw, 2))


def apply_treasury_cap(daily_issued: float, requested_ncr: float) -> tuple[float, float]:
    """
    Treasury cap damping uygula.
    Returns: (final_ncr, capped_amount)
    """
    if requested_ncr <= 0:
        return 0.0, 0.0

    projected = daily_issued + requested_ncr
    load_ratio = projected / TREASURY_DAILY_LIMIT if TREASURY_DAILY_LIMIT > 0 else 0.0

    # Get damping multiplier
    thresholds = sorted(TREASURY_DAMPING_TABLE.items(), key=lambda x: x[0])
    multiplier = 1.0
    for threshold, mult in thresholds:
        if load_ratio <= threshold:
            multiplier = mult
            break
    else:
        multiplier = 0.05  # Overflow

    final_ncr = round(requested_ncr * multiplier, 2)
    capped = requested_ncr - final_ncr

    return final_ncr, capped


# -----------------------------
# HELPERS: NCR PRICE & COVERAGE
# -----------------------------


def compute_coverage_ratio(treasury_fiat: float, ncr_outstanding: float, ncr_price: float) -> float:
    if ncr_outstanding <= 0 or ncr_price <= 0:
        return 2.0
    liability = ncr_outstanding * ncr_price
    if liability <= 0:
        return 2.0
    return treasury_fiat / liability


def ema(prev: float, new: float, alpha: float) -> float:
    return alpha * new + (1 - alpha) * prev


def update_ncr_price(state: EconomyState, net_mint: float, net_burn: float, net_redeem: float) -> None:
    """
    Basitleştirilmiş fiyat stabilizasyonu.
    """
    raw_cov = compute_coverage_ratio(
        state.treasury_reserves_fiat,
        state.ncr_outstanding,
        state.ncr_price_try,
    )
    raw_flow = (net_mint - net_burn - net_redeem) / 100_000.0

    state.ema_coverage = ema(state.ema_coverage, raw_cov, SMOOTHING_ALPHA)
    state.ema_flow_index = ema(state.ema_flow_index, raw_flow, SMOOTHING_ALPHA)

    cov_diff = state.ema_coverage - TARGET_COVERAGE
    cov_adjust = K_COVERAGE * cov_diff
    flow_adjust = -K_FLOW * state.ema_flow_index

    total_adj = cov_adjust + flow_adjust

    if total_adj > MAX_DAILY_PRICE_CHANGE:
        total_adj = MAX_DAILY_PRICE_CHANGE
    elif total_adj < -MAX_DAILY_PRICE_CHANGE:
        total_adj = -MAX_DAILY_PRICE_CHANGE

    new_price = state.ncr_price_try * (1 + total_adj)

    # bantlar
    new_price = max(0.3, min(3.0, new_price))
    state.ncr_price_try = round(new_price, 4)


# -----------------------------
# HELPERS: BASE NCR & TASK COUNT
# -----------------------------


def sample_base_ncr() -> float:
    """
    Görev tipi dağılımına göre base NCR seç.
    Kolay / orta / zor / elite basit mix.
    """
    r = random.random()
    if r < 0.50:
        return random.choice([2.0, 3.0, 4.0])  # basit görevler
    elif r < 0.85:
        return random.choice([5.0, 6.0, 8.0])  # orta görevler
    elif r < 0.97:
        return random.choice([10.0, 12.0, 15.0])  # zor görevler
    else:
        return random.choice([20.0, 25.0])  # elite jackpot tadı, ama formül frenliyor


def sample_task_count_for_user() -> int:
    """
    Günde kullanıcı başı kaç görev deniyor?
    Çoğu 0–2, az bir kısmı 3.
    """
    return random.choices(
        population=[0, 1, 2, 3],
        weights=[0.4, 0.3, 0.2, 0.1],
        k=1,
    )[0]


# -----------------------------
# SIMULATION CORE
# -----------------------------


def init_users(n: int) -> List[UserState]:
    users: List[UserState] = []
    for _ in range(n):
        level = random.randint(1, 6)  # lansman anında düşük level
        streak = 0
        # kalite dağılımı: çoğu 60–80 civarı
        siyah_score = random.gauss(75, 10)
        siyah_score = max(40.0, min(100.0, siyah_score))
        # risk: çoğu 0–3 arası
        risk_score = max(0.0, min(10.0, random.gauss(1.5, 1.5)))

        users.append(UserState(level=level, streak=streak, siyah_score=siyah_score, risk_score=risk_score))
    return users


def run_simulation(
    n_users: int = N_USERS,
    n_days: int = N_DAYS,
) -> Dict:
    users = init_users(n_users)
    econ = EconomyState(
        treasury_reserves_fiat=INITIAL_TREASURY_RESERVES,
        ncr_outstanding=0.0,
        ncr_price_try=INITIAL_NCR_PRICE,
        daily_issued_ncr=0.0,
    )

    day_stats: List[DayStats] = []

    for day in range(1, n_days + 1):
        # Reset daily issued
        econ.daily_issued_ncr = 0.0

        total_minted = 0.0
        total_burned = 0.0
        total_redeemed = 0.0
        total_capped = 0.0

        for u in users:
            n_tasks = sample_task_count_for_user()
            earned_today = 0.0

            for _ in range(n_tasks):
                base_ncr = sample_base_ncr()
                reward_ncr = compute_final_ncr_for_task(u, base_ncr)

                # Treasury Cap uygula
                capped_ncr, capped_amount = apply_treasury_cap(econ.daily_issued_ncr, reward_ncr)
                econ.daily_issued_ncr += capped_ncr
                total_capped += capped_amount

                # AbuseGuard etkisi: bazen risk_score'u zıplat
                if reward_ncr == 0 and base_ncr > 0:
                    # kötü içerik gibi
                    u.risk_score = min(10.0, u.risk_score + random.uniform(0.5, 1.5))

                if capped_ncr > 0:
                    earned_today += capped_ncr

            # kullanıcıya ekle
            u.balance_ncr += earned_today
            total_minted += earned_today

            # günlük behavior sonrası stat güncelle
            u.update_after_day(did_any_task=(n_tasks > 0))

        # burn & redemption simüle et
        total_burned = econ.ncr_outstanding * BURN_RATE
        total_redeemed = (econ.ncr_outstanding + total_minted - total_burned) * REDEMPTION_RATE

        # sınır koy
        total_burned = min(total_burned, econ.ncr_outstanding + total_minted)
        total_redeemed = min(total_redeemed, econ.ncr_outstanding + total_minted - total_burned)

        net_mint = total_minted
        net_burn = total_burned
        net_redeem = total_redeemed

        # NCR supply update
        econ.ncr_outstanding += net_mint - net_burn - net_redeem
        econ.ncr_outstanding = max(0.0, econ.ncr_outstanding)

        # Treasury fiat update (redemption)
        econ.treasury_reserves_fiat -= total_redeemed * econ.ncr_price_try
        if econ.treasury_reserves_fiat < 0:
            econ.treasury_reserves_fiat = 0.0

        # Fiyat güncelle
        update_ncr_price(econ, net_mint=net_mint, net_burn=net_burn, net_redeem=net_redeem)

        coverage = compute_coverage_ratio(
            econ.treasury_reserves_fiat,
            econ.ncr_outstanding,
            econ.ncr_price_try,
        )

        treasury_load = econ.daily_issued_ncr / TREASURY_DAILY_LIMIT if TREASURY_DAILY_LIMIT > 0 else 0.0

        day_stats.append(
            DayStats(
                day=day,
                total_minted_ncr=round(total_minted, 2),
                total_burned_ncr=round(total_burned, 2),
                total_redeemed_ncr=round(total_redeemed, 2),
                treasury_reserves_fiat=round(econ.treasury_reserves_fiat, 2),
                ncr_outstanding=round(econ.ncr_outstanding, 2),
                ncr_price_try=econ.ncr_price_try,
                coverage_ratio=round(coverage, 3),
                treasury_load_ratio=round(treasury_load, 3),
                treasury_capped_ncr=round(total_capped, 2),
            )
        )

    return {
        "days": day_stats,
        "users": users,
        "economy": econ,
    }


# -----------------------------
# MAIN / RAPOR
# -----------------------------


def print_summary(sim_result: Dict):
    days: List[DayStats] = sim_result["days"]
    users: List[UserState] = sim_result["users"]
    econ: EconomyState = sim_result["economy"]

    total_minted = sum(d.total_minted_ncr for d in days)
    total_redeemed = sum(d.total_redeemed_ncr for d in days)
    total_capped = sum(d.treasury_capped_ncr for d in days)

    avg_daily_mint = total_minted / len(days)
    avg_daily_redeem = total_redeemed / len(days)

    balances = [u.balance_ncr for u in users]
    avg_balance = mean(balances)
    top_10 = sorted(balances, reverse=True)[:10]

    print("\n" + "=" * 70)
    print("NasipQuest Economy Simulation Summary")
    print("=" * 70 + "\n")
    print(f"Kullanıcı sayısı        : {len(users):,}")
    print(f"Simülasyon süresi      : {len(days)} gün")
    print(f"Toplam NCR mint        : {total_minted:,.2f}")
    print(f"Toplam NCR redemption  : {total_redeemed:,.2f}")
    print(f"Toplam Treasury capped : {total_capped:,.2f}")
    print(f"Avg günlük mint        : {avg_daily_mint:,.2f} NCR")
    print(f"Avg günlük redemption  : {avg_daily_redeem:,.2f} NCR\n")

    last = days[-1]
    print(f"Son gün Treasury (fiat): {last.treasury_reserves_fiat:,.2f}")
    print(f"Son gün NCR supply     : {last.ncr_outstanding:,.2f}")
    print(f"Son gün NCR fiyatı     : {last.ncr_price_try:.4f} TRY")
    print(f"Son gün coverage ratio : {last.coverage_ratio:.3f}")
    print(f"Son gün Treasury yük   : {last.treasury_load_ratio:.1%}\n")

    print(f"Kullanıcı başı ort. NCR: {avg_balance:.2f}")
    print(f"Top 10 NCR holder      : {[round(v, 2) for v in top_10]}\n")

    print("İlk 5 gün:")
    print(f"{'Gün':>4} | {'Mint':>12} | {'Redeem':>12} | {'Treasury':>12} | {'Price':>8} | {'Cov':>6} | {'Load':>6}")
    print("-" * 70)
    for d in days[:5]:
        print(
            f"{d.day:4d} | {d.total_minted_ncr:12,.0f} | {d.total_redeemed_ncr:12,.0f} | "
            f"{d.treasury_reserves_fiat:12,.0f} | {d.ncr_price_try:8.4f} | {d.coverage_ratio:6.3f} | {d.treasury_load_ratio:6.1%}"
        )

    print("\nSon 5 gün:")
    print(f"{'Gün':>4} | {'Mint':>12} | {'Redeem':>12} | {'Treasury':>12} | {'Price':>8} | {'Cov':>6} | {'Load':>6}")
    print("-" * 70)
    for d in days[-5:]:
        print(
            f"{d.day:4d} | {d.total_minted_ncr:12,.0f} | {d.total_redeemed_ncr:12,.0f} | "
            f"{d.treasury_reserves_fiat:12,.0f} | {d.ncr_price_try:8.4f} | {d.coverage_ratio:6.3f} | {d.treasury_load_ratio:6.1%}"
        )

    print("\n" + "=" * 70)
    print("✅ Simülasyon tamamlandı!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    random.seed(42)  # deterministik debug için
    result = run_simulation()
    print_summary(result)

