# Aurora Justice Policy Versions

Bu dokümantasyon, Aurora Justice Stack'in policy versiyonlarını, değişikliklerini ve simülasyon/gerçek kullanım gözlemlerini kaydeder.

## Policy Versioning Format

Her versiyon için:
- **Policy Parameters**: CP weights, decay rates, regime thresholds
- **Simulation Results**: Simüle edilmiş kullanıcı davranışları ve sonuçlar
- **Real Usage Observations**: Gerçek kullanım verilerinden gözlemler
- **Rationale**: Neden bu policy seçildi?

---

## Aurora Justice Policy v1.0

**Date**: 2024-12-01  
**Status**: Initial Release

### Policy Parameters

```python
DECAY_PER_DAY = 1.0

CP_BASE_WEIGHTS = {
    "EKO": 10,
    "COM": 15,
    "SYS": 20,
    "TRUST": 25,
}

SEVERITY_MULTIPLIER = {
    1: 0.5,
    2: 1.0,
    3: 1.5,
    4: 2.0,
    5: 3.0,
}

REGIME_THRESHOLDS = {
    "SOFT_FLAG": 20,
    "PROBATION": 40,
    "RESTRICTED": 60,
    "LOCKDOWN": 80,
}
```

### Simulation Results

**Test Parameters:**
- Users: 2000
- Days: 90
- Decay per day: 1.0
- Violation probability: 0.05 (5% daily)

**Results:**
```
Final Regime Distribution:
- NORMAL:     71.2%
- SOFT_FLAG:  14.5%
- PROBATION:   8.3%
- RESTRICTED:  4.1%
- LOCKDOWN:    1.9%

Average CP: 8.7
Median CP:  3.0

Top Violation Categories:
- COM:   46%
- TRUST: 28%
- SYS:   16%
- EKO:   10%
```

**Assessment:**
- ✓ LOCKDOWN rate (1.9%) - Within acceptable range
- ✓ NORMAL rate (71.2%) - Balanced distribution
- Policy appears balanced for initial release

### Real Usage Observations

**Period**: 2024-12-01 – 2025-01-01 (31 days)

**Metrics:**
- Total users: 1,234
- Lockdown users: 15 (1.2%)
- Recall requests: 5 (0.4%)
- Average CP: 7.3

**Top Violations:**
- `COM_TOXIC`: 45% of violations
- `TRUST_FRAUD`: 22% of violations
- `SYS_EXPLOIT`: 18% of violations
- `EKO_NO_SHOW`: 15% of violations

**Observations:**
- COM violations dominate - suggests need for better communication guidelines
- TRUST violations higher than expected - may need stricter identity verification
- Overall system stability good, no major abuse patterns detected

### Rationale

Initial policy designed to be:
- **Balanced**: Not too strict to discourage users, not too lenient to allow abuse
- **Observable**: Clear regime transitions allow users to understand consequences
- **Recoverable**: Decay mechanism allows users to improve behavior over time

---

## Aurora Justice Policy v1.1 (Proposed)

**Date**: TBD  
**Status**: Under Review

### Proposed Changes

**Issue**: COM violations are too frequent (46% in sim, 45% in real usage)

**Proposed Adjustments:**
```python
# Option A: Increase COM base weight
CP_BASE_WEIGHTS["COM"] = 18  # was 15

# Option B: Increase decay rate
DECAY_PER_DAY = 1.2  # was 1.0

# Option C: Adjust regime thresholds
REGIME_THRESHOLDS["PROBATION"] = 35  # was 40 (earlier intervention)
```

### Simulation Comparison

**Test Parameters:**
- Users: 2000
- Days: 90
- Decay per day: 1.2
- Violation probability: 0.05

**Results (Option B - Increased Decay):**
```
Final Regime Distribution:
- NORMAL:     75.8% (+4.6%)
- SOFT_FLAG:  12.1% (-2.4%)
- PROBATION:   7.1% (-1.2%)
- RESTRICTED:  3.5% (-0.6%)
- LOCKDOWN:    1.5% (-0.4%)

Average CP: 6.2 (-2.5)
```

**Assessment:**
- ✓ Lower average CP - users recover faster
- ✓ Slightly higher NORMAL rate - more users in good standing
- ✓ Lower LOCKDOWN rate - fewer permanent restrictions
- **Recommendation**: Implement Option B (increased decay)

---

## Policy Tuning Guidelines

### When to Update Policy

1. **High LOCKDOWN Rate (>5%)**
   - Policy may be too strict
   - Consider: Lower thresholds, higher decay, lower CP weights

2. **Very High NORMAL Rate (>90%)**
   - Policy may be too lenient
   - Consider: Higher CP weights, lower decay, stricter thresholds

3. **Category Imbalance**
   - One category dominates violations
   - Consider: Category-specific adjustments

4. **User Feedback**
   - Users report unfair treatment
   - Consider: Review specific cases, adjust weights

### Testing New Policies

1. **Run Simulation**
   ```bash
   python scripts/simulate_aurora_policies.py \
     --users 2000 \
     --days 90 \
     --decay 1.2 \
     --output sim_v1.1.json \
     --summary
   ```

2. **Compare Results**
   - Regime distribution changes
   - Average CP changes
   - Lockdown rate changes

3. **A/B Test (if possible)**
   - Deploy to subset of users
   - Monitor real metrics
   - Compare with simulation

4. **Document Decision**
   - Add new version to this document
   - Include rationale
   - Track real usage after deployment

---

## Metrics to Monitor

### Key Performance Indicators

1. **Regime Distribution**
   - Target: 70-80% NORMAL
   - Alert if: NORMAL < 60% or > 90%

2. **Lockdown Rate**
   - Target: 1-3%
   - Alert if: Lockdown > 5%

3. **Average CP**
   - Target: 5-15
   - Alert if: Average CP > 20

4. **Violation Categories**
   - Monitor for category spikes
   - Investigate if one category > 50%

5. **Recall Requests**
   - Target: < 1%
   - Alert if: Recall > 2% (trust issue)

---

## Version History

| Version | Date | Key Changes | Status |
|---------|------|-------------|--------|
| v1.0 | 2024-12-01 | Initial release | ✅ Active |
| v1.1 | TBD | Increased decay rate | 🔄 Proposed |

---

## Notes

- Policy changes should be backward compatible when possible
- Always run simulations before deploying policy changes
- Monitor real usage metrics for at least 2 weeks after policy update
- Document all changes and rationale in this document

