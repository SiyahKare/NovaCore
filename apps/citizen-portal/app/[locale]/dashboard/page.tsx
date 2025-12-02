'use client'

import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { ProtectedView } from '@/components/ProtectedView'
import { useCitizenState, useRegimeTheme, usePolicy } from '@aurora/hooks'
import {
  NovaScoreCard,
  RegimeBadge,
  PolicyBreakdown,
  CPTrendGraph,
  RegimeBanner,
  AuroraStateHealth,
  CitizenTimeline,
  TrustFactors,
} from '@aurora/ui'
import type { NovaScorePayload, CpState, PolicyParams } from '@aurora/ui'
import Link from 'next/link'

export default function DashboardPage() {
  return (
    <ProtectedView>
      <DashboardInner />
    </ProtectedView>
  )
}

function DashboardInner() {
  const t = useTranslations('dashboard')
  const citizenState = useCitizenState()
  const regimeTheme = useRegimeTheme()
  const policy = usePolicy()

  // ... existing dashboard code ...
  // (Copy the rest from app/dashboard/page.tsx)

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{t('title')}</h1>
      {/* Rest of dashboard content */}
    </div>
  )
}

