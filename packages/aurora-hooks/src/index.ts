// Aurora Hooks Library
// Shared React hooks for Aurora API integration

export { useAuroraAPI } from './useAuroraAPI'
export { useNovaScore } from './useNovaScore'
export { useJustice } from './useJustice'
export { useEnforcementError } from './useEnforcementError'
export { useConsentFlow } from './useConsentFlow'
export { usePolicy } from './usePolicy'
export { useCurrentCitizen, type CitizenIdentity } from './useCurrentCitizen'
export { useAdminViolations, type AdminViolation, type AdminViolationFilters, type ViolationCategory } from './useAdminViolations'
export { useAuroraEvents } from './useAuroraEvents'
export { useGrowthMetrics, type GrowthMetrics } from './useGrowthMetrics'
export { useAcademyProgress, type AcademyProgress, type ModuleProgress } from './useAcademyProgress'
export { useCitizenState, type CitizenState, type WalletBalance, type LoyaltyProfile, type PrivacyProfile, type ViolationItem } from './useCitizenState'
export { useRegimeTheme, type AuroraRegime, type RegimeTheme } from './useRegimeTheme'
export { useHitlQuests, type HitlQuest } from './useHitlQuests'
export {
  useTelegramConversations,
  useTelegramConversation,
  useTelegramLead,
  useTelegramStats,
  type Conversation,
  type Lead,
  type HandoffEvent,
  type LeadSegment,
  type ContactChannel,
  type Message,
} from './useTelegramConversations'
export {
  useOmbudsmanAppeals,
  useOmbudsmanViolations,
  useOmbudsmanDecision,
  type PendingAppeal,
  type PendingViolation,
  type DecisionRequest,
  type DecisionResponse,
} from './useOmbudsman'

