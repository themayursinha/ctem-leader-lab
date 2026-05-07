import { useEffect, useState } from 'react';

import { api } from '../api';

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
              <strong>{risk.ctem_score}</strong>
              <span>CTEM score</span>
            </div>
            <div className="risk-body">
              <div className="card-header">
                <div>
                  <h2>{risk.title}</h2>
                  <p>{risk.description}</p>
                </div>
                <DecisionBadge value={risk.decision} />
              </div>
              <div className="risk-meta">
                <span>{risk.exposure_type}</span>
                <span>{risk.severity} source severity</span>
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
