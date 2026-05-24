import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts'

import { api } from '../api'
import Skeleton from '../components/Skeleton'
import type { MaturityDomain, ProgramSummary } from '../types/api'

const ErrorState = ({ error }: { error: Error }) => (
  <div className="notice-panel error">
    <strong>Unable to load data.</strong> The backend may not be running or there may be a connection issue.
    <div className="error-detail">{error.message}</div>
  </div>
)

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

export default Dashboard
