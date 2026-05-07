import { useEffect, useState } from 'react';

import { api } from '../api';

const Scoping = () => {
  const [services, setServices] = useState([]);
  const [assets, setAssets] = useState([]);
  const [artifacts, setArtifacts] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([api.getBusinessServices(), api.getAssets(), api.getWorkshopArtifacts()])
      .then(([serviceData, assetData, artifactData]) => {
        setServices(serviceData);
        setAssets(assetData);
        setArtifacts(artifactData);
      })
      .catch(setError);
  }, []);

  if (error) return <div className="notice-panel error">Unable to load scoping data. {error.message}</div>;
  if (!artifacts) return <div className="notice-panel">Loading crown-jewel scope...</div>;

  const assetsById = Object.fromEntries(assets.map((asset) => [asset.id, asset]));

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Stage 1</p>
          <h1 className="page-title">Scoping</h1>
          <p className="page-intro">
            Start with business services, crown jewels, owners, and risk appetite. Scanner coverage comes later.
          </p>
        </div>
      </section>

      <section className="service-grid">
        {services.map((service) => (
          <article className={`service-card ${service.in_scope ? 'in-scope' : ''}`} key={service.id}>
            <div className="card-header">
              <div>
                <span className="eyebrow">{service.criticality} service</span>
                <h2>{service.name}</h2>
              </div>
              <span className={`badge ${service.in_scope ? 'decision-act' : 'decision-track'}`}>
                {service.in_scope ? 'In scope' : 'Track'}
              </span>
            </div>
            <p>{service.description}</p>
            <dl className="detail-list">
              <div><dt>Executive</dt><dd>{service.executive_owner}</dd></div>
              <div><dt>Owner</dt><dd>{service.business_owner}</dd></div>
              <div><dt>Risk appetite</dt><dd>{service.risk_appetite}</dd></div>
              <div><dt>Scope reason</dt><dd>{service.scope_reason}</dd></div>
            </dl>
            <div className="chip-row">
              {service.crown_jewel_asset_ids.length > 0 ? (
                service.crown_jewel_asset_ids.map((assetId) => (
                  <span className="chip" key={assetId}>{assetsById[assetId]?.name || assetId}</span>
                ))
              ) : (
                <span className="chip muted-chip">No crown jewels in first sprint</span>
              )}
            </div>
          </article>
        ))}
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Crown-Jewel Worksheet</h2>
          <p>Use this workshop sequence to turn business priorities into CTEM scope.</p>
        </div>
        <div className="prompt-grid">
          {artifacts.crown_jewel_worksheet.map((prompt, index) => (
            <div className="prompt-card" key={prompt}>
              <span>{index + 1}</span>
              <p>{prompt}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Scoped Asset Inventory</h2>
          <p>Assets are grouped by service so leaders can see ownership before remediation starts.</p>
        </div>
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Service</th>
                <th>Owner</th>
                <th>Exposure</th>
                <th>Crown jewel</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr key={asset.id}>
                  <td><strong>{asset.name}</strong><span>{asset.type}</span></td>
                  <td>{services.find((service) => service.id === asset.service_id)?.name}</td>
                  <td>{asset.owner}</td>
                  <td>{asset.reachable_from_internet}</td>
                  <td>{asset.crown_jewel ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
};

export default Scoping;
