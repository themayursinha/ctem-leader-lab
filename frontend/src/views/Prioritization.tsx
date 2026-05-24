import { useEffect, useState } from 'react'
import type { ComponentType } from 'react'

import { api } from '../api'
import Skeleton from '../components/Skeleton'
import Tooltip from '../components/Tooltip'
import type { PrioritizedExposure } from '../types/api'

const PrioritizationLoading = () => (
  <div className="page-stack">
    <section className="page-header">
      <Skeleton width="80px" height="0.75rem" />
      <Skeleton width="200px" height="2rem" margin="4px 0 0" />
      <Skeleton width="100%" height="1rem" margin="12px 0 0" />
    </section>
    <section className="comparison-strip">
      <Skeleton width="100%" height="4rem" />
    </section>
    <section className="risk-list">
      {[1, 2, 3].map((i) => (
        <div className="risk-card" key={i}>
          <div className="risk-score">
            <Skeleton width="48px" height="2rem" />
            <Skeleton width="80px" height="0.78rem" margin="8px 0 0" />
          </div>
          <div className="risk-body">
            <Skeleton width="80%" height="1rem" />
            <Skeleton width="60%" height="0.85rem" margin="8px 0 0" />
            <Skeleton width="100%" height="3rem" margin="16px 0 0" />
          </div>
        </div>
      ))}
    </section>
  </div>
)

interface PrioritizationProps {
  DecisionBadge: ComponentType<{ value: string }>
}

const Prioritization = ({ DecisionBadge }: PrioritizationProps) => {
  const [risks, setRisks] = useState<PrioritizedExposure[]>([])
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    api.getPrioritizedExposures()
      .then(setRisks)
      .catch(setError)
  }, [])

  if (error) return <div className="notice-panel error"><strong>Unable to load prioritization data.</strong> The backend may be unavailable.<div className="error-detail">{error.message}</div></div>
  if (!risks.length) return <PrioritizationLoading />

  const mediumSecret = risks.find((risk) => risk.exposure_id === 'exp-ci-token')
  const isolatedCve = risks.find((risk) => risk.exposure_id === 'exp-dev-wiki-cve')

  const decisionTooltip: Record<string, string> = {
    Act: 'Immediate remediation required — active threat or critical business impact.',
    Attend: 'High priority — remediate in the current sprint cycle.',
    Monitor: 'Track closely — no immediate action but conditions may change.',
    Track: 'Low priority — accepted for now, re-evaluate in future cycles.',
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Stage 3</p>
          <h1 className="page-title">Prioritization</h1>
          <p className="page-intro">
            Rank exposures by business impact, attacker utility, validation evidence, and mobilization feasibility.
          </p>
        </div>
      </section>

      <section className="comparison-strip">
        <div>
          <span className="eyebrow">CTEM behavior</span>
          <h2>Context beats raw severity</h2>
          <p>
            The medium-severity leaked token scores {mediumSecret?.ctem_score}, while the isolated high-CVSS wiki issue scores {isolatedCve?.ctem_score}.
            That is the point: CTEM protects remediation capacity for credible paths to business harm.
          </p>
        </div>
      </section>

      <section className="risk-list">
        {risks.map((risk) => (
          <article className="risk-card" key={risk.exposure_id}>
            <div className="risk-score">
              <Tooltip label="Composite score (0–100) based on business impact, attacker utility, validation confidence, and feasibility">
                <strong>{risk.ctem_score}</strong>
              </Tooltip>
              <span>CTEM score</span>
            </div>
            <div className="risk-body">
              <div className="card-header">
                <div>
                  <h2>{risk.title}</h2>
                  <p>{risk.description}</p>
                </div>
                <Tooltip label={decisionTooltip[risk.decision] || ''}>
                  <DecisionBadge value={risk.decision} />
                </Tooltip>
              </div>
              <div className="risk-meta">
                <Tooltip label="Source domain of the exposure finding">
                  <span>{risk.exposure_type}</span>
                </Tooltip>
                <Tooltip label="Original severity rating from the source system">
                  <span>{risk.severity} source severity</span>
                </Tooltip>
                <span>{risk.owner}</span>
                <span>{risk.sla}</span>
                <span>{risk.source || 'Seed data'}</span>
                <span>Validated {risk.validated_at || 'not recorded'}</span>
              </div>
              <p className="rationale">{risk.rationale}</p>
              <p className="why">{risk.why_it_matters}</p>
              <div className="driver-grid">
                {risk.score_drivers.map((driver) => (
                  <div className="driver" key={driver.name}>
                    <strong>{driver.value}</strong>
                    <span>{driver.name}</span>
                    <p>{driver.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

export default Prioritization
