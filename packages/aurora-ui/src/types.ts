// Aurora UI Types
// Shared type definitions for Aurora frontend ecosystem

export type Regime = 'NORMAL' | 'SOFT_FLAG' | 'PROBATION' | 'RESTRICTED' | 'LOCKDOWN'

export interface CpState {
  user_id: string
  cp_value: number
  last_updated_at: string
  regime: Regime
}

export interface NovaScoreComponent {
  value: number
  confidence: number
}

export interface NovaScoreComponents {
  ECO: NovaScoreComponent
  REL: NovaScoreComponent
  SOC: NovaScoreComponent
  ID: NovaScoreComponent
  CON: NovaScoreComponent
}

export interface NovaScorePayload {
  value: number
  components: NovaScoreComponents
  confidence_overall: number
  explanation?: string | null
}

export interface PolicyParams {
  version: string
  decay_per_day: number
  base_eko: number
  base_com: number
  base_sys: number
  base_trust: number
  threshold_soft_flag: number
  threshold_probation: number
  threshold_restricted: number
  threshold_lockdown: number
  onchain_block?: number | null
  onchain_tx?: string | null
  synced_at: string
}

export interface EnforcementError {
  error: 'AURORA_ENFORCEMENT'
  detail: string
  regime: Regime
  action: string
  allowed_actions?: string[]
  appeal_url?: string
}

export interface ViolationLog {
  id: string
  user_id: string
  category: 'EKO' | 'COM' | 'SYS' | 'TRUST'
  code: string
  severity: number
  cp_delta: number
  source?: string | null
  created_at: string
}

export interface PrivacyProfile {
  user_id: string
  latest_consent_id?: string | null
  contract_version?: string | null
  consent_level?: 'FULL' | 'LIMITED' | 'MINIMUM' | null
  recall_mode?: 'ANONYMIZE' | 'FULL_EXCLUDE' | null
  recall_requested_at?: string | null
  last_policy_updated_at?: string | null
}

