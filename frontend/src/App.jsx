import { useEffect, useState } from 'react';
import { HashRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  Activity,
  ClipboardList,
  Crosshair,
  LayoutDashboard,
  ListOrdered,
  Search,
  ShieldAlert,
  Workflow,
} from 'lucide-react';

import { api } from './api';
import Discovery from './views/Discovery';
import Mobilization from './views/Mobilization';
import Prioritization from './views/Prioritization';
import Scoping from './views/Scoping';
import Validation from './views/Validation';
import WorkshopPack from './views/WorkshopPack';

const LoadingState = ({ label = 'Loading CTEM data...' }) => (
  <div className="notice-panel">{label}</div>
);

const ErrorState = ({ error }) => (
  <div className="notice-panel error">Unable to load CTEM data. {error.message}</div>
);

const DecisionBadge = ({ value }) => (
  <span className={`badge decision-${String(value).toLowerCase()}`}>{value}</span>
);

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [maturity, setMaturity] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getProgramSummary(), api.getMaturity()])
      .then(([summaryData, maturityData]) => {
        setSummary(summaryData);
        setMaturity(maturityData);
      })
      .catch(setError);
  }, []);

  if (error) return <ErrorState error={error} />;
  if (!summary) return <LoadingState label="Loading CTEM operating model..." />;

  const metricCards = [
    ['Scoped services', summary.metrics.scoped_services],
    ['Crown-jewel assets', summary.metrics.crown_jewel_assets],
    ['Act decisions', summary.metrics.act_decisions],
    ['Validated paths', summary.metrics.validated_attack_paths],
  ];

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
            {summary.cycle.map((stage, index) => (
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
          <div className="maturity-stack">
            {maturity.map((domain) => (
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
          {summary.operating_principles.map((principle) => (
            <div className="principle-card" key={principle}>{principle}</div>
          ))}
        </div>
      </section>
    </div>
  );
};

const SidebarItem = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  return (
    <Link to={to} className={`nav-item ${isActive ? 'active' : ''}`}>
      <Icon size={20} />
      <span>{label}</span>
    </Link>
  );
};

function App() {
  return (
    <Router>
      <div className="app-container">
        <aside className="sidebar">
          <div className="sidebar-header">
            <h1><ShieldAlert size={22} /> CTEM Leader Lab</h1>
            <p>Exposure reduction workbench</p>
          </div>
          <nav className="sidebar-nav">
            <SidebarItem to="/" icon={LayoutDashboard} label="Dashboard" />
            <div className="nav-section-label">CTEM Stages</div>
            <SidebarItem to="/scoping" icon={Crosshair} label="1. Scoping" />
            <SidebarItem to="/discovery" icon={Search} label="2. Discovery" />
            <SidebarItem to="/prioritization" icon={ListOrdered} label="3. Prioritization" />
            <SidebarItem to="/validation" icon={Activity} label="4. Validation" />
            <SidebarItem to="/mobilization" icon={Workflow} label="5. Mobilization" />
            <div className="nav-section-label">Takeaway</div>
            <SidebarItem to="/workshop-pack" icon={ClipboardList} label="Workshop Pack" />
          </nav>
        </aside>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scoping" element={<Scoping />} />
            <Route path="/discovery" element={<Discovery />} />
            <Route path="/prioritization" element={<Prioritization DecisionBadge={DecisionBadge} />} />
            <Route path="/validation" element={<Validation />} />
            <Route path="/mobilization" element={<Mobilization DecisionBadge={DecisionBadge} />} />
            <Route path="/workshop-pack" element={<WorkshopPack />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
