import { useEffect, useState } from 'react';

import { api } from '../api';
import Skeleton from '../components/Skeleton';

const ValidationLoading = () => (
  <div className="page-stack">
    <section className="page-header">
      <Skeleton width="80px" height="0.75rem" />
      <Skeleton width="200px" height="2rem" margin="4px 0 0" />
      <Skeleton width="100%" height="1rem" margin="12px 0 0" />
    </section>
    <section className="path-stack">
      {[1, 2].map((i) => (
        <div className="path-card" key={i}>
          <Skeleton width="60%" height="1.1rem" />
          <Skeleton width="80%" height="0.85rem" margin="8px 0 0" />
          <Skeleton width="100%" height="6rem" margin="16px 0 0" />
        </div>
      ))}
    </section>
  </div>
);

const Validation = () => {
  const [paths, setPaths] = useState([]);
  const [artifacts, setArtifacts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getAttackPaths(), api.getWorkshopArtifacts()])
      .then(([pathData, artifactData]) => {
        setPaths(pathData);
        setArtifacts(artifactData);
      })
      .catch(setError);
  }, []);

  if (error) return <div className="notice-panel error"><strong>Unable to load validation data.</strong> The backend may be unavailable.<div className="error-detail">{error.message}</div></div>;
  if (!artifacts) return <ValidationLoading />;

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Stage 4</p>
          <h1 className="page-title">Validation</h1>
          <p className="page-intro">
            Prove exploitability, reachability, control performance, and blast radius safely before mobilizing scarce teams.
          </p>
        </div>
      </section>

      <section className="path-stack">
        {paths.map((path) => (
          <article className="path-card" key={path.id}>
            <div className="card-header">
              <div>
                <span className="eyebrow">{path.status} path</span>
                <h2>{path.name}</h2>
                <p>{path.objective}</p>
              </div>
              <span className={`badge decision-${path.status === 'Validated' ? 'act' : 'attend'}`}>
                {path.evidence_confidence} confidence
              </span>
            </div>
            <div className="path-detail-grid">
              <div>
                <span>Blast radius</span>
                <p>{path.blast_radius}</p>
              </div>
              <div>
                <span>Safe validation</span>
                <p>{path.safe_validation_method}</p>
              </div>
            </div>
            <div className="path-steps">
              {path.steps.map((step) => (
                <div className="path-step" key={`${path.id}-${step.order}`}>
                  <span>{step.order}</span>
                  <h3>{step.title}</h3>
                  <p>{step.technique}</p>
                  <small>{step.validation}</small>
                  <small>{step.control_gap}</small>
                </div>
              ))}
            </div>
          </article>
        ))}
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Evidence Pack</h2>
          <p>Every Act or Attend decision needs enough evidence for a resolver team and an executive sponsor.</p>
        </div>
        <div className="prompt-grid">
          {artifacts.validation_evidence_pack.map((item, index) => (
            <div className="prompt-card" key={item}>
              <span>{index + 1}</span>
              <p>{item}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Validation;
