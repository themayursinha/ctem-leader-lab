import { useEffect, useRef, useState } from 'react'
import { HashRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  Activity,
  Book,
  Bookmark,
  ClipboardList,
  Crosshair,
  LayoutDashboard,
  ListOrdered,
  Menu,
  Search,
  ShieldAlert,
  Workflow,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts'

import { api } from './api'
import Breadcrumbs from './components/Breadcrumbs'
import ErrorBoundary from './components/ErrorBoundary'
import Skeleton from './components/Skeleton'
import { ToastProvider } from './components/Toast'
import Discovery from './views/Discovery'
import Guide from './views/Guide'
import Mobilization from './views/Mobilization'
import Prioritization from './views/Prioritization'
import Scoping from './views/Scoping'
import Validation from './views/Validation'
import Sessions from './views/Sessions'
import WorkshopPack from './views/WorkshopPack'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const WELCOME_KEY = 'ctem-welcome-dismissed'
const BANNER_KEY = 'ctem-demo-banner-dismissed'

const ErrorState = ({ error }: { error: Error }) => (
  <div className="notice-panel error">
    <strong>Unable to load data.</strong> The backend may not be running or there may be a connection issue.
    <div className="error-detail">{error.message}</div>
  </div>
)

const DecisionBadge = ({ value }: { value: string }) => (
  <span className={`badge decision-${String(value).toLowerCase()}`}>{value}</span>
)

const WelcomeModal = () => {
  const [visible, setVisible] = useState(!localStorage.getItem(WELCOME_KEY))
  const welcomeRef = useRef<HTMLHeadingElement>(null)

  useEffect(() => {
    if (visible) welcomeRef.current?.focus()
  }, [visible])

  const dismiss = () => {
    localStorage.setItem(WELCOME_KEY, 'true')
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="modal-overlay" onClick={dismiss}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-label="Welcome">
        <h2 tabIndex={-1} ref={welcomeRef}>Welcome to CTEM Leader Lab</h2>
        <p className="modal-subtitle">An interactive workbench for security leaders moving from vulnerability management to Continuous Threat Exposure Management.</p>
        <div className="modal-features">
          <div className="modal-feature">
            <strong>Five CTEM Stages</strong>
            <span>Navigate Scoping, Discovery, Prioritization, Validation, and Mobilization from the sidebar.</span>
          </div>
          <div className="modal-feature">
            <strong>Pre-loaded Demo</strong>
            <span>The app ships with realistic but fictional data so you can explore every feature immediately.</span>
          </div>
          <div className="modal-feature">
            <strong>Sessions &amp; Export</strong>
            <span>Save your workspace, load previous sessions, export CSVs, and generate executive summaries.</span>
          </div>
          <div className="modal-feature">
            <strong>Workshop Pack</strong>
            <span>Generate a facilitator-ready takeaway with templates and a 30/60/90-day roadmap.</span>
          </div>
        </div>
        <p className="modal-hint">Start with the <strong>Dashboard</strong> for a program overview, then follow the stages in order.</p>
        <button className="tool-button modal-cta" onClick={dismiss}>Get started</button>
      </div>
    </div>
  )
}

const DemoBanner = () => {
  const [visible, setVisible] = useState(!localStorage.getItem(BANNER_KEY))

  const dismiss = () => {
    localStorage.setItem(BANNER_KEY, 'true')
    setVisible(false)
  }

  if (!visible) return null

  return (
    <div className="demo-banner" role="alert">
      <span>This is a demo with fictional data. Use it to explore CTEM workflows — no real systems or data are connected.</span>
      <button className="demo-banner-close" onClick={dismiss} aria-label="Dismiss demo notice">&times;</button>
    </div>
  )
}

const DashboardLoading = () => (
  <div className="page-stack">
    <section className="page-header">
      <div>
        <Skeleton width="100px" height="0.75rem" />
        <Skeleton width="280px" height="2rem" margin="8px 0 0" />
        <Skeleton width="100%" height="1rem" margin="12px 0 0" />
      </div>
    </section>
    <section className="metric-grid">
      {[1, 2, 3, 4].map((i) => (
        <div className="metric-card" key={i}>
          <Skeleton width="80px" height="0.85rem" />
          <Skeleton width="60px" height="1.8rem" margin="8px 0 0" />
        </div>
      ))}
    </section>
  </div>
)

import type { MaturityDomain, ProgramSummary } from './types/api'

const Dashboard = () => {
  const [summary, setSummary] = useState<ProgramSummary | null>(null)
  const [maturity, setMaturity] = useState<MaturityDomain[]>([])
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    Promise.all([api.getProgramSummary(), api.getMaturity()])
      .then(([summaryData, maturityData]) => {
        setSummary(summaryData)
        setMaturity(maturityData)
      })
      .catch(setError)
  }, [])

  if (error) return <ErrorState error={error} />
  if (!summary) return <DashboardLoading />

  const metricCards: [string, string | number][] = [
    ['Scoped services', summary.metrics.scoped_services],
    ['Crown-jewel assets', summary.metrics.crown_jewel_assets],
    ['Act decisions', summary.metrics.act_decisions],
    ['Validated paths', summary.metrics.validated_attack_paths],
  ]

  const chartData = maturity.map((d: MaturityDomain) => ({ name: d.name.split(' ')[0], score: d.score }))

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">CTEM Leader Lab</p>
          <h1 className="page-title">{summary.organization}</h1>
          <p className="page-intro">{summary.goal}</p>
        </div>
        <div className="summary-callout">
          <span className="muted">90-day target</span>
          <strong>{summary.metrics.exposure_reduction_goal}</strong>
        </div>
      </section>

      <section className="metric-grid">
        {metricCards.map(([label, value]) => (
          <div className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </section>

      <section className="split-grid">
        <div className="content-section">
          <div className="section-heading">
            <h2>Operating Cycle</h2>
            <p>Each CTEM stage answers a leadership question before the next handoff.</p>
          </div>
          <div className="cycle-list">
            {summary.cycle.map((stage: { stage: string; leader_question: string }, index: number) => (
              <div className="cycle-item" key={stage.stage}>
                <span className="cycle-index">{index + 1}</span>
                <div>
                  <h3>{stage.stage}</h3>
                  <p>{stage.leader_question}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="content-section">
          <div className="section-heading">
            <h2>Program Maturity</h2>
            <p>
              Current average {summary.maturity_current}/5, target {summary.maturity_target}/5.
            </p>
          </div>
          <div className="maturity-chart">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: -10 }}>
                <XAxis dataKey="name" tick={{ fill: '#a8b0bd', fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis domain={[0, 5]} ticks={[0, 1, 2, 3, 4, 5]} tick={{ fill: '#a8b0bd', fontSize: 11 }} axisLine={false} tickLine={false} />
                <RechartsTooltip
                  contentStyle={{ background: '#20242b', border: '1px solid #353b45', borderRadius: 6, fontSize: 13 }}
                  labelStyle={{ color: '#f4f6f8' }}
                />
                <Bar dataKey="score" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="maturity-stack">
            {maturity.map((domain: MaturityDomain) => (
              <div className="maturity-row" key={domain.name}>
                <div className="maturity-label">
                  <span>{domain.name}</span>
                  <strong>{domain.score}/5</strong>
                </div>
                <div className="progress-track">
                  <div className="progress-fill" style={{ width: `${domain.score * 20}%` }} />
                </div>
                <p>{domain.next_step}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Leadership Principles</h2>
          <p>Use these as guardrails when moving away from vulnerability-management habits.</p>
        </div>
        <div className="principle-grid">
          {summary.operating_principles.map((principle: string) => (
            <div className="principle-card" key={principle}>{principle}</div>
          ))}
        </div>
      </section>
    </div>
  )
}

interface SidebarItemProps {
  to: string
  icon: React.ElementType
  label: string
  onClick: () => void
}

const SidebarItem = ({ to, icon: Icon, label, onClick }: SidebarItemProps) => {
  const location = useLocation()
  const isActive = location.pathname === to
  return (
    <Link to={to} className={`nav-item ${isActive ? 'active' : ''}`} onClick={onClick} aria-current={isActive ? 'page' : undefined}>
      <Icon size={20} aria-hidden="true" />
      <span>{label}</span>
    </Link>
  )
}

const AppContent = () => {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const mainRef = useRef<HTMLElement>(null)
  const menuRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    mainRef.current?.focus()
  }, [location.pathname])

  useEffect(() => {
    if (sidebarOpen) {
      menuRef.current?.focus()
    }
  }, [sidebarOpen])

  return (
    <div className="app-container">
      <button className="skip-link" onClick={() => mainRef.current?.focus()}>
        Skip to content
      </button>

      <button
        className="hamburger"
        onClick={() => setSidebarOpen((prev) => !prev)}
        aria-label={sidebarOpen ? 'Close navigation menu' : 'Open navigation menu'}
        aria-expanded={sidebarOpen}
        ref={menuRef}
      >
        <Menu size={22} />
      </button>

      {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-header">
          <h1><ShieldAlert size={22} aria-hidden="true" /> CTEM Leader Lab</h1>
          <p>Exposure reduction workbench</p>
        </div>
        <nav className="sidebar-nav">
          <SidebarItem to="/" icon={LayoutDashboard} label="Dashboard" onClick={() => setSidebarOpen(false)} />
          <div className="nav-section-label">CTEM Stages</div>
          <SidebarItem to="/scoping" icon={Crosshair} label="1. Scoping" onClick={() => setSidebarOpen(false)} />
          <SidebarItem to="/discovery" icon={Search} label="2. Discovery" onClick={() => setSidebarOpen(false)} />
          <SidebarItem to="/prioritization" icon={ListOrdered} label="3. Prioritization" onClick={() => setSidebarOpen(false)} />
          <SidebarItem to="/validation" icon={Activity} label="4. Validation" onClick={() => setSidebarOpen(false)} />
          <SidebarItem to="/mobilization" icon={Workflow} label="5. Mobilization" onClick={() => setSidebarOpen(false)} />
          <div className="nav-section-label">Takeaway</div>
          <SidebarItem to="/workshop-pack" icon={ClipboardList} label="Workshop Pack" onClick={() => setSidebarOpen(false)} />
          <div className="nav-section-label">Workspace</div>
          <SidebarItem to="/sessions" icon={Bookmark} label="Sessions" onClick={() => setSidebarOpen(false)} />
          <div className="nav-section-label">Reference</div>
          <SidebarItem to="/guide" icon={Book} label="User Guide" onClick={() => setSidebarOpen(false)} />
        </nav>
      </aside>

      <main className="main-content" ref={mainRef} tabIndex={-1}>
        <DemoBanner />
        <Breadcrumbs pathname={location.pathname} />
        <WelcomeModal />
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scoping" element={<Scoping />} />
            <Route path="/discovery" element={<Discovery />} />
            <Route path="/prioritization" element={<Prioritization DecisionBadge={DecisionBadge} />} />
            <Route path="/validation" element={<Validation />} />
            <Route path="/mobilization" element={<Mobilization DecisionBadge={DecisionBadge} />} />
            <Route path="/workshop-pack" element={<WorkshopPack />} />
            <Route path="/sessions" element={<Sessions />} />
            <Route path="/guide" element={<Guide />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <ToastProvider>
          <AppContent />
        </ToastProvider>
      </Router>
    </QueryClientProvider>
  )
}

export default App
