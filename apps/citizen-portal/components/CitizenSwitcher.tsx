'use client'

import { setToken, clearToken } from '@/lib/auth'

const DEV_USERS = [
  { id: 'AUR-SIGMA', label: 'Sigma Citizen' },
  { id: 'AUR-TROLLER', label: 'Troller Citizen' },
  { id: 'AUR-GHOST', label: 'Ghost Citizen' },
]

export function CitizenSwitcher() {
  // Only show in dev mode
  if (process.env.NEXT_PUBLIC_AURORA_ENV !== 'dev' && process.env.NODE_ENV !== 'development') {
    return null
  }

  const handleSelect = async (id: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_AURORA_API_URL || 'http://localhost:8000/api/v1'
      const res = await fetch(`${apiUrl}/dev/token?user_id=${id}`, {
        method: 'POST',
      })
      if (res.ok) {
        const { token } = await res.json()
        setToken(token)
        window.location.reload()
      } else {
        const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
        alert(`Failed to get token: ${error.detail || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Token fetch error:', error)
      alert('Failed to get token. Make sure backend is running and in dev mode.')
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 rounded-xl border border-white/15 bg-black/80 backdrop-blur-sm px-3 py-2 text-[11px] text-gray-300 shadow-lg">
      <div className="mb-1 text-[10px] text-gray-500 uppercase tracking-[0.2em]">
        Dev · Switch Citizen
      </div>
      <div className="flex flex-wrap gap-2">
        {DEV_USERS.map((u) => (
          <button
            key={u.id}
            onClick={() => handleSelect(u.id)}
            className="rounded-lg border border-white/15 px-2 py-1 hover:bg-white/5 transition"
          >
            {u.label}
          </button>
        ))}
        <button
          onClick={() => {
            clearToken()
            window.location.reload()
          }}
          className="rounded-lg border border-red-500/40 px-2 py-1 text-red-300 hover:bg-red-500/10 transition"
        >
          Logout
        </button>
      </div>
    </div>
  )
}

