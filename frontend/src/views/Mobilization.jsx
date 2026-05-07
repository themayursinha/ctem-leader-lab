import { useEffect, useState } from 'react';

import { api } from '../api';

const Mobilization = ({ DecisionBadge }) => {
  const [actions, setActions] = useState([]);
  const [artifacts, setArtifacts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getRemediationActions(), api.getWorkshopArtifacts()])
      .then(([actionData, artifactData]) => {
        setActions(actionData);
        setArtifacts(artifactData);
      })
      .catch(setError);
  }, []);

  if (error) return <div className="notice-panel error">Unable to load mobilization data. {error.message}</div>;
  if (!artifacts) return <div className="notice-panel">Loading mobilization board...</div>;

  const statuses = ['To Do', 'In Progress', 'Done', 'Accepted Risk'];

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Stage 5</p>
          <h1 className="page-title">Mobilization</h1>
          <p className="page-intro">
            CTEM succeeds when validated exposures become owned work with SLAs, retest criteria, and exception rules.
          </p>
        </div>
      </section>

      <section className="board">
        {statuses.map((status) => {
          const columnActions = actions.filter((action) => action.status === status);
          return (
            <div className="board-column" key={status}>
              <div className="column-header">
                <h2>{status}</h2>
                <span>{columnActions.length}</span>
              </div>
              <div className="action-stack">
                {columnActions.map((action) => (
                  <article className="action-card" key={action.id}>
                    <div className="card-header">
                      <strong>{action.id}</strong>
                      <DecisionBadge value={action.priority} />
                    </div>
                    <h3>{action.title}</h3>
                    <p>{action.playbook}</p>
                    <dl className="mini-detail-list">
                      <div><dt>Owner</dt><dd>{action.owner}</dd></div>
                      <div><dt>SLA</dt><dd>{action.sla}</dd></div>
                      <div><dt>Due</dt><dd>{action.due_in_days === 0 ? 'Complete' : `${action.due_in_days} days`}</dd></div>
                      <div><dt>Retest</dt><dd>{action.retest_status}</dd></div>
                    </dl>
                    {action.risk_acceptance_required && <span className="risk-acceptance">Risk acceptance required</span>}
                  </article>
                ))}
              </div>
            </div>
          );
        })}
      </section>

      <section className="split-grid">
        <div className="content-section">
          <div className="section-heading">
            <h2>RACI</h2>
            <p>Make ownership explicit before the exposure ages.</p>
          </div>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Role</th>
                  <th>Responsibility</th>
                </tr>
              </thead>
              <tbody>
                {artifacts.raci.map((row) => (
                  <tr key={row.role}>
                    <td><strong>{row.role}</strong></td>
                    <td>{row.responsibility}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="content-section">
          <div className="section-heading">
            <h2>30/60/90 Roadmap</h2>
            <p>A first-quarter path from agreement to validated reduction.</p>
          </div>
          <div className="roadmap">
            {artifacts.roadmap_30_60_90.map((item) => (
              <div className="roadmap-item" key={item.window}>
                <span>{item.window}</span>
                <h3>{item.outcome}</h3>
                <p>{item.actions}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Mobilization;
