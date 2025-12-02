import React from 'react'

interface CPTrendGraphProps {
  data: Array<{ date: string; cp: number }>
  className?: string
}

export const CPTrendGraph: React.FC<CPTrendGraphProps> = ({ data, className = '' }) => {
  if (data.length === 0) {
    return (
      <div className={`aurora-card ${className}`}>
        <p className="text-sm text-slate-400">No CP history available</p>
      </div>
    )
  }

  const maxCp = Math.max(...data.map((d) => d.cp), 100)

  return (
    <div className={`aurora-card ${className}`}>
      <h3 className="text-lg font-semibold text-slate-200 mb-4">CP Trend</h3>
      <div className="relative h-48">
        <svg className="w-full h-full" viewBox="0 0 400 200" preserveAspectRatio="none">
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((y) => (
            <line
              key={y}
              x1="0"
              y1={200 - (y / maxCp) * 200}
              x2="400"
              y2={200 - (y / maxCp) * 200}
              stroke="rgba(148, 163, 184, 0.1)"
              strokeWidth="1"
            />
          ))}

          {/* CP line */}
          <polyline
            points={data
              .map(
                (d, i) =>
                  `${(i / (data.length - 1)) * 400},${200 - (d.cp / maxCp) * 200}`
              )
              .join(' ')}
            fill="none"
            stroke="#8b5cf6"
            strokeWidth="2"
            className="drop-shadow-lg"
          />

          {/* CP area fill */}
          <polygon
            points={`0,200 ${data
              .map(
                (d, i) =>
                  `${(i / (data.length - 1)) * 400},${200 - (d.cp / maxCp) * 200}`
              )
              .join(' ')} 400,200`}
            fill="url(#cpGradient)"
            opacity="0.2"
          />

          <defs>
            <linearGradient id="cpGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>

        {/* Labels */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-slate-500 px-2">
          <span>{data[0]?.date.split('T')[0]}</span>
          <span>{data[data.length - 1]?.date.split('T')[0]}</span>
        </div>
      </div>

      <div className="mt-4 flex justify-between text-sm">
        <div>
          <span className="text-slate-400">Current: </span>
          <span className="text-aurora-purple font-semibold">{data[data.length - 1]?.cp}</span>
        </div>
        <div>
          <span className="text-slate-400">Peak: </span>
          <span className="text-red-400 font-semibold">{maxCp}</span>
        </div>
      </div>
    </div>
  )
}

