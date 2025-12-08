import Link from 'next/link'
import {  } from 'next/navigation'

interface ModuleCardProps {
  slug: string
  title: string
  level: string
  minutes: number
  description: string
  completed?: boolean
  viewed?: boolean
}

export function ModuleCard(props: ModuleCardProps) {
  const { slug, title, level, minutes, description, completed, viewed } = props

  return (
    <Link
      href={`/academy/modules/${slug}`}
      className={`group rounded-2xl border p-4 transition flex flex-col justify-between ${
        completed
          ? 'border-emerald-500/60 bg-emerald-500/5'
          : viewed
          ? 'border-purple-500/40 bg-purple-500/5'
          : 'border-white/10 bg-white/5 hover:border-purple-500/60 hover:bg-purple-500/5'
      }`}
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-gray-100">{title}</h2>
            {completed && (
              <span className="text-emerald-400 text-sm" title="Tamamlandı">
                ✓
              </span>
            )}
          </div>
          <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] text-gray-300">
            {level}
          </span>
        </div>
        <p className="text-xs text-gray-400">{description}</p>
      </div>

      <div className="mt-4 flex items-center justify-between text-[11px] text-gray-400">
        <span>⏱ {minutes} dakika</span>
        <span className={`group-hover:translate-x-1 transition ${
          completed ? 'text-emerald-300' : 'text-purple-300'
        }`}>
          {completed ? 'Tekrar aç →' : 'Dersi aç →'}
        </span>
      </div>
    </Link>
  )
}

