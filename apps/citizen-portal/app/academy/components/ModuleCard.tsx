import Link from 'next/link'

interface ModuleCardProps {
  slug: string
  title: string
  level: string
  minutes: number
  description: string
}

export function ModuleCard(props: ModuleCardProps) {
  const { slug, title, level, minutes, description } = props

  return (
    <Link
      href={`/academy/modules/${slug}`}
      className="group rounded-2xl border border-white/10 bg-white/5 p-4 hover:border-purple-500/60 hover:bg-purple-500/5 transition flex flex-col justify-between"
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-gray-100">{title}</h2>
          <span className="rounded-full border border-white/10 px-2 py-0.5 text-[10px] text-gray-300">
            {level}
          </span>
        </div>
        <p className="text-xs text-gray-400">{description}</p>
      </div>

      <div className="mt-4 flex items-center justify-between text-[11px] text-gray-400">
        <span>⏱ {minutes} dakika</span>
        <span className="text-purple-300 group-hover:translate-x-1 transition">Dersi aç →</span>
      </div>
    </Link>
  )
}

