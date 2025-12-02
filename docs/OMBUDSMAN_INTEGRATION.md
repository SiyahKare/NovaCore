# Ombudsman / Operator Console Integration

## Overview

The Aurora Case File endpoint provides a complete view of a user's status in the Aurora State Network. This is designed for operator consoles, admin panels, and ombudsman interfaces.

## Endpoint

```
GET /justice/case/{user_id}
```

**Authentication:** Required (JWT token)

**Authorization:** Should be restricted to admin/ombudsman roles (TODO: implement role check)

## Response Structure

```json
{
  "user_id": "AUR-TEST-1",
  "privacy_profile": {
    "user_id": "AUR-TEST-1",
    "latest_consent_id": "uuid-here",
    "contract_version": "Aurora-DataEthics-v1.0",
    "policy": {
      "behavioral": { "allowed": true, "purposes": [...] },
      "performance": { "allowed": true, "purposes": [...] },
      "economy": { "allowed": true, "purposes": [...] },
      "redline": { "allowed": true, "purposes": [...] }
    },
    "consent_level": "FULL",
    "recall_requested_at": null,
    "recall_mode": null,
    "last_policy_updated_at": "2025-12-01T10:00:00Z"
  },
  "cp_state": {
    "user_id": "AUR-TEST-1",
    "cp_value": 45,
    "regime": "PROBATION",
    "last_updated_at": "2025-12-01T10:00:00Z"
  },
  "nova_score": {
    "value": 750,
    "components": {
      "ECO": { "value": 80.0, "confidence": 1.0 },
      "REL": { "value": 70.0, "confidence": 1.0 },
      "SOC": { "value": 65.0, "confidence": 1.0 },
      "ID": { "value": 75.0, "confidence": 1.0 },
      "CON": { "value": 60.0, "confidence": 1.0 }
    },
    "confidence_overall": 1.0,
    "explanation": "NovaScore explanation text..."
  },
  "recent_violations": [
    {
      "id": "uuid-here",
      "user_id": "AUR-TEST-1",
      "category": "COM",
      "code": "COM_TOXIC",
      "severity": 3,
      "cp_delta": 22,
      "source": "chat-moderation",
      "created_at": "2025-12-01T09:00:00Z"
    }
  ]
}
```

## Use Cases

### 1. Operator Console - User Investigation

When an operator needs to investigate why a user is restricted:

```typescript
// Frontend example (TypeScript/React)
const fetchUserCase = async (userId: string) => {
  const response = await fetch(`/justice/case/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const caseFile = await response.json();
  
  // Display in UI
  return {
    regime: caseFile.cp_state.regime,
    cpValue: caseFile.cp_state.cp_value,
    violations: caseFile.recent_violations,
    novaScore: caseFile.nova_score.value,
    consentStatus: caseFile.privacy_profile.consent_level
  };
};
```

### 2. Admin Panel - User Management

Display user status in admin panel:

```typescript
interface UserCaseDisplay {
  userId: string;
  regime: 'NORMAL' | 'SOFT_FLAG' | 'PROBATION' | 'RESTRICTED' | 'LOCKDOWN';
  cpValue: number;
  novaScore: number;
  violationCount: number;
  consentLevel: string;
}

const UserCaseCard = ({ userId }: { userId: string }) => {
  const [caseFile, setCaseFile] = useState<UserCaseDisplay | null>(null);
  
  useEffect(() => {
    fetchUserCase(userId).then(setCaseFile);
  }, [userId]);
  
  if (!caseFile) return <Loading />;
  
  return (
    <Card>
      <Badge regime={caseFile.regime}>{caseFile.regime}</Badge>
      <div>CP: {caseFile.cpValue}</div>
      <div>NovaScore: {caseFile.novaScore}</div>
      <div>Violations: {caseFile.violationCount}</div>
    </Card>
  );
};
```

### 3. Ombudsman - Appeal Review

When reviewing user appeals:

```typescript
const AppealReview = ({ userId }: { userId: string }) => {
  const caseFile = useCaseFile(userId);
  
  return (
    <div>
      <h2>User Appeal Review: {userId}</h2>
      
      <Section title="Current Status">
        <RegimeBadge regime={caseFile.cp_state.regime} />
        <p>CP Value: {caseFile.cp_state.cp_value}</p>
        <p>NovaScore: {caseFile.nova_score.value}</p>
      </Section>
      
      <Section title="Violations">
        {caseFile.recent_violations.map(v => (
          <ViolationCard key={v.id} violation={v} />
        ))}
      </Section>
      
      <Section title="Consent Status">
        <p>Level: {caseFile.privacy_profile.consent_level}</p>
        <p>Contract: {caseFile.privacy_profile.contract_version}</p>
      </Section>
    </div>
  );
};
```

## Regime Display Guidelines

### Regime Badges

- **NORMAL**: Green badge, "Normal"
- **SOFT_FLAG**: Yellow badge, "Yumuşak Uyarı"
- **PROBATION**: Orange badge, "Gözaltı"
- **RESTRICTED**: Red badge, "Kısıtlı"
- **LOCKDOWN**: Dark red badge, "Kilitli"

### CP Value Display

- 0-19: Green indicator
- 20-39: Yellow indicator
- 40-59: Orange indicator
- 60-79: Red indicator
- 80+: Dark red indicator

## Integration Checklist

- [ ] Add authentication middleware
- [ ] Add role-based authorization (admin/ombudsman only)
- [ ] Create frontend component for case file display
- [ ] Add regime badge component
- [ ] Add violation history table
- [ ] Add NovaScore visualization
- [ ] Add consent status display
- [ ] Add action buttons (appeal, review, etc.)

## Error Handling

```typescript
try {
  const caseFile = await fetchUserCase(userId);
} catch (error) {
  if (error.status === 404) {
    // User not found
  } else if (error.status === 403) {
    // Not authorized (not admin/ombudsman)
  } else {
    // Other error
  }
}
```

## Future Enhancements

1. **Timeline View**: Show CP changes over time
2. **Violation Details**: Expandable violation cards with full context
3. **Appeal System**: Direct appeal submission from case file
4. **Notes**: Operator notes on user case
5. **Export**: PDF export of case file for records

