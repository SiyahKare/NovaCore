import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { AuroraCasePage } from './features/justice/AuroraCasePage'
import { AuroraStatsPanel } from './features/justice/AuroraStatsPanel'
import { SendMessageForm } from './features/flirtmarket/SendMessageForm'
import { RegimeBadge } from './features/justice/RegimeBadge'
import { RegimeBanner } from './features/justice/RegimeBanner'

function App() {
  // Demo token - gerçek uygulamada auth store'dan gelecek
  const demoToken = 'demo-token'

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-bold text-sky-400">Aurora Justice Stack</h1>
              <p className="text-xs text-slate-400">NovaCore Frontend Demo</p>
            </div>
            <nav className="flex gap-4">
              <Link
                to="/"
                className="px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/stats"
                className="px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Stats
              </Link>
              <Link
                to="/case/AUR-TEST-1"
                className="px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              >
                Case File
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Routes>
          <Route
            path="/"
            element={
              <div className="space-y-8">
                <div>
                  <h2 className="text-2xl font-semibold mb-4">Dashboard</h2>
                  
                  {/* Demo Regime Banner */}
                  <div className="mb-6">
                    <RegimeBanner
                      regime="PROBATION"
                      cp={45}
                      onDismiss={() => console.log('Banner dismissed')}
                    />
                  </div>

                  {/* Demo Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-6">
                      <h3 className="text-sm font-semibold text-slate-400 mb-2">
                        Mesaj Gönder
                      </h3>
                      <SendMessageForm
                        recipientId="performer-123"
                        recipientName="Luna"
                        token={demoToken}
                        onSuccess={() => alert('Mesaj gönderildi!')}
                      />
                    </div>

                    <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-6">
                      <h3 className="text-sm font-semibold text-slate-400 mb-4">
                        Regime Badge Örnekleri
                      </h3>
                      <div className="space-y-3">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">NORMAL:</span>
                          <RegimeBadge regime="NORMAL" cp={0} size="sm" showTooltip />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">SOFT_FLAG:</span>
                          <RegimeBadge regime="SOFT_FLAG" cp={25} size="sm" showTooltip />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">PROBATION:</span>
                          <RegimeBadge regime="PROBATION" cp={45} size="sm" showTooltip />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">RESTRICTED:</span>
                          <RegimeBadge regime="RESTRICTED" cp={70} size="sm" showTooltip />
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-slate-400">LOCKDOWN:</span>
                          <RegimeBadge regime="LOCKDOWN" cp={90} size="sm" showTooltip />
                        </div>
                      </div>
                    </div>

                    <div className="bg-slate-900/60 border border-slate-700/70 rounded-2xl p-6">
                      <h3 className="text-sm font-semibold text-slate-400 mb-2">
                        Hızlı Linkler
                      </h3>
                      <div className="space-y-2 text-sm">
                        <Link
                          to="/case/AUR-SIGMA"
                          className="block text-sky-400 hover:text-sky-300"
                        >
                          → AUR-SIGMA Case File
                        </Link>
                        <Link
                          to="/case/AUR-TROLLER"
                          className="block text-sky-400 hover:text-sky-300"
                        >
                          → AUR-TROLLER Case File
                        </Link>
                        <Link
                          to="/case/AUR-GHOST"
                          className="block text-sky-400 hover:text-sky-300"
                        >
                          → AUR-GHOST Case File
                        </Link>
                        <Link
                          to="/stats"
                          className="block text-sky-400 hover:text-sky-300"
                        >
                          → Aurora Stats
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            }
          />
          <Route path="/stats" element={<AuroraStatsPanel token={demoToken} />} />
          <Route path="/case/:userId" element={<AuroraCasePage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-6 text-center text-xs text-slate-500">
          Aurora Justice Stack v2.0 - NovaCore Frontend Demo
        </div>
      </footer>
    </div>
  )
}

export default App

