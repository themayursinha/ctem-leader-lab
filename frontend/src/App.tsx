import { lazy, Suspense, useEffect, useRef, useState } from 'react'
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
  LogOut,
  Menu,
  Search,
  ShieldAlert,
  Workflow,
} from 'lucide-react'

import Breadcrumbs from './components/Breadcrumbs'
import ErrorBoundary from './components/ErrorBoundary'
import Skeleton from './components/Skeleton'
import { ToastProvider } from './components/Toast'
import { useAuthStore } from './store'

const Dashboard = lazy(() => import('./views/Dashboard'))
const Discovery = lazy(() => import('./views/Discovery'))
const Guide = lazy(() => import('./views/Guide'))
const Login = lazy(() => import('./views/Login'))
const Mobilization = lazy(() => import('./views/Mobilization'))
const Prioritization = lazy(() => import('./views/Prioritization'))
const Register = lazy(() => import('./views/Register'))
const Scoping = lazy(() => import('./views/Scoping'))
const Validation = lazy(() => import('./views/Validation'))
const Sessions = lazy(() => import('./views/Sessions'))
const WorkshopPack = lazy(() => import('./views/WorkshopPack'))

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

const PageLoader = () => (
  <div className="page-stack">
    <section className="page-header">
      <Skeleton width="180px" height="1rem" />
      <Skeleton width="240px" height="1.6rem" margin="8px 0 0" />
    </section>
    <section className="metric-grid">
      {[1, 2, 3].map((i) => (
        <div className="metric-card" key={i}>
          <Skeleton width="70px" height="0.75rem" />
          <Skeleton width="50px" height="1.5rem" margin="8px 0 0" />
        </div>
      ))}
    </section>
  </div>
)

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
  const { user, clearAuth, isAuthenticated } = useAuthStore()

  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  useEffect(() => {
    mainRef.current?.focus()
  }, [location.pathname])

  useEffect(() => {
    if (sidebarOpen) {
      menuRef.current?.focus()
    }
  }, [sidebarOpen])

  if (isAuthPage) {
    return (
      <div className="app-container">
        <ErrorBoundary>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </div>
    )
  }

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
          {isAuthenticated() && (
            <>
              <div className="nav-section-label">Account</div>
              <div className="sidebar-user">
                <span className="sidebar-user-name">{user?.name || user?.email}</span>
                <button
                  className="tool-button compact"
                  type="button"
                  onClick={() => clearAuth()}
                  aria-label="Sign out"
                >
                  <LogOut size={14} />
                  <span>Sign out</span>
                </button>
              </div>
            </>
          )}
        </nav>
      </aside>

      <main className="main-content" ref={mainRef} tabIndex={-1}>
        <DemoBanner />
        <Breadcrumbs pathname={location.pathname} />
        <WelcomeModal />
        <ErrorBoundary>
          <Suspense fallback={<PageLoader />}>
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
          </Suspense>
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
