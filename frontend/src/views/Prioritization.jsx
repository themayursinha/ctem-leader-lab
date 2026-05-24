import { useEffect, useState } from 'react';

import { api } from '../api';
import Tooltip from '../components/Tooltip';

const Prioritization = ({ DecisionBadge }) => {
  const [risks, setRisks] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getPrioritizedExposures()
      .then(setRisks)
      .catch(setError);
  }, []);

  if (error) return <div className="notice-panel error">Unable to load prioritization data. {error.message}</div>;
  if (!risks.length) return <div className="notice-panel">Calculating CTEM decision outcomes...</div>;

  const mediumSecret = risks.find((risk) => risk.exposure_id === 'exp-ci-token');
  const isolatedCve = risks.find((risk) => risk.exposure_id === 'exp-dev-wiki-cve');

  const decisionTooltip = {
    act: 'Immediate remediation required — active threat or critical business impact.',
    attend: 'High priority — remediate in the current sprint cycle.',
    monitor: 'Track closely — no immediate action but conditions may change.',
    track: 'Low priority — accepted for now, re-evaluate in future cycles.',
  };

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
                <Tooltip label={decisionTooltip[risk.decision.toLowerCase()] || ''}>
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
  );
};

export default Prioritization;
