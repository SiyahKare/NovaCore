# Aurora Metrics & Statistics

## Overview

Aurora Justice Stack now includes comprehensive metrics and statistics for monitoring system health, policy effectiveness, and user behavior patterns.

## API Endpoint

### `GET /api/v1/admin/aurora/stats`

**Authentication:** Admin only (`is_admin: true`)

**Response:**
```json
{
  "total_consent_records": 1234,
  "total_privacy_profiles": 1200,
  "recall_requests_count": 45,
  "recall_requests_last_24h": 2,
  "consent_signatures_last_24h": 15,
  "total_violations": 567,
  "violations_last_24h": 8,
  "violations_last_7d": 42,
  "violation_breakdown": {
    "EKO": 120,
    "COM": 250,
    "SYS": 150,
    "TRUST": 47
  },
  "average_cp": 12.5,
  "regime_distribution": {
    "NORMAL": 1100,
    "SOFT_FLAG": 50,
    "PROBATION": 30,
    "RESTRICTED": 15,
    "LOCKDOWN": 5
  },
  "lockdown_users_count": 5,
  "generated_at": "2024-12-01T12:00:00Z"
}
```

## Frontend Component

### `AuroraStatsPanel`

```tsx
import { AuroraStatsPanel } from "@/features/justice/AuroraStatsPanel";

function AdminDashboard() {
  const token = useAuthStore((state) => state.token);
  
  return (
    <div>
      <AuroraStatsPanel token={token} />
    </div>
  );
}
```

**Features:**
- Auto-refreshes every 60 seconds
- Real-time statistics
- Visual regime distribution
- Violation category breakdown
- 24h/7d trend indicators

## Policy Simulation

### `scripts/simulate_aurora_policies.py`

Simulates user behavior and CP/regime evolution over time to help tune policy parameters.

**Usage:**
```bash
# Basic simulation
python scripts/simulate_aurora_policies.py --users 1000 --days 90

# Custom parameters
python scripts/simulate_aurora_policies.py \
  --users 2000 \
  --days 180 \
  --decay 1.5 \
  --violation-prob 0.03 \
  --output simulation_results.json

# Summary only (no user details)
python scripts/simulate_aurora_policies.py \
  --users 1000 \
  --days 90 \
  --summary-only
```

**Parameters:**
- `--users`: Number of users to simulate (default: 1000)
- `--days`: Number of days to simulate (default: 90)
- `--decay`: CP decay per day (default: 1.0)
- `--violation-prob`: Daily violation probability per user (default: 0.05 = 5%)
- `--output`: Output JSON file (default: aurora_simulation.json)
- `--summary-only`: Only output summary statistics

**Output:**
```json
{
  "simulation_params": {
    "num_users": 1000,
    "days": 90,
    "decay_per_day": 1.0,
    "violation_probability": 0.05
  },
  "summary": {
    "total_users": 1000,
    "average_cp": 15.23,
    "max_cp": 95,
    "total_violations": 4500,
    "average_violations_per_user": 4.5,
    "regime_distribution": {
      "NORMAL": 850,
      "SOFT_FLAG": 80,
      "PROBATION": 50,
      "RESTRICTED": 15,
      "LOCKDOWN": 5
    },
    "lockdown_users": 5,
    "lockdown_percentage": 0.5,
    "restricted_users": 15,
    "restricted_percentage": 1.5,
    "probation_users": 50,
    "probation_percentage": 5.0
  }
}
```

## Use Cases

### 1. Policy Tuning

Run simulation with different parameters to find optimal CP weights and decay rates:

```bash
# Test different decay rates
for decay in 0.5 1.0 1.5 2.0; do
  python scripts/simulate_aurora_policies.py \
    --users 1000 \
    --days 90 \
    --decay $decay \
    --output "sim_decay_${decay}.json" \
    --summary-only
done
```

### 2. Health Monitoring

Monitor real-time stats to detect anomalies:

- **High LOCKDOWN rate** → Policy too strict or abuse spike
- **High recall requests** → Trust/consent issue
- **Violation spike** → System abuse or policy gap

### 3. Trend Analysis

Track metrics over time:
- Average CP trend
- Regime distribution changes
- Violation category shifts

## Integration with Prometheus/Grafana

Future enhancement: Export metrics to Prometheus format:

```python
# Example Prometheus metrics
aurora_total_consent_records{environment="production"} 1234
aurora_lockdown_users{environment="production"} 5
aurora_average_cp{environment="production"} 12.5
aurora_violations_last_24h{environment="production"} 8
```

## Next Steps

1. **Time-series data**: Store historical stats for trend analysis
2. **Alerting**: Set thresholds for critical metrics
3. **Dashboard**: Build Grafana dashboard with Aurora metrics
4. **Export**: Add Prometheus metrics endpoint

