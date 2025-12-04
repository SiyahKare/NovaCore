'use client';

import { ReactNode } from 'react';
import { NovaCoreNav } from './NovaCoreNav';
import { CitizenSwitcher } from './CitizenSwitcher';
import { useRegimeTheme } from '@aurora/hooks';

interface NovaCoreShellProps {
  children: ReactNode;
}

export function NovaCoreShell({ children }: NovaCoreShellProps) {
  const theme = useRegimeTheme();

  return (
    <div className={`min-h-screen text-gray-100 ${theme.bgClass} transition-colors duration-700`}>
      <div className="min-h-screen flex flex-col">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
          <NovaCoreNav />
        </div>

        <main className="flex-1">
          <div className={`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 ${theme.glowClass}`}>
            {children}
          </div>
        </main>

        <CitizenSwitcher />

        {theme.regime === 'LOCKDOWN' && (
          <div className="pointer-events-none fixed inset-0 bg-black/45 backdrop-blur-[1px] mix-blend-multiply z-40" />
        )}
      </div>
    </div>
  );
}

