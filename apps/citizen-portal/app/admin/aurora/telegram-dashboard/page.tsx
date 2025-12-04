'use client'

import { TelegramConsoleLayout } from '@/components/aurora-contact/TelegramConsoleLayout'
import { dummyConversations, dummyLeads, dummyHandoffs } from '@/lib/aurora-contact/dummy-data'
import type { Conversation, Lead, HandoffEvent } from '@aurora/hooks'

export default function TelegramDashboardPage() {
  // MVP: server component + client child; gerçek veride SWR/React Query bağlanır
  return (
    <TelegramConsoleLayout
      conversations={dummyConversations}
      leads={dummyLeads}
      handoffs={dummyHandoffs}
    />
  )
}

