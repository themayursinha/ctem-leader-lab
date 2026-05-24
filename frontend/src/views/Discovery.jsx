import { useEffect, useMemo, useState } from 'react';

import { api } from '../api';
import CsvToolbar from '../components/CsvToolbar';
import Skeleton from '../components/Skeleton';
import TableSearch from '../components/TableSearch';
import Tooltip from '../components/Tooltip';

const DiscoveryLoading = () => (
  <div className="page-stack">
    <section className="page-header">
      <div>
        <Skeleton width="80px" height="0.75rem" />
        <Skeleton width="200px" height="2rem" margin="4px 0 0" />
        <Skeleton width="100%" height="1rem" margin="12px 0 0" />
      </div>
    </section>
    <section className="metric-grid">
      {[1, 2, 3, 4].map((i) => (
        <div className="metric-card compact" key={i}>
          <Skeleton width="60px" height="0.85rem" />
          <Skeleton width="40px" height="1.4rem" margin="8px 0 0" />
        </div>
      ))}
    </section>
    <section className="content-section">
      <Skeleton width="180px" height="1.1rem" />
      <Skeleton width="100%" height="16rem" margin="16px 0 0" />
    </section>
  </div>
);

const Discovery = () => {
  const [exposures, setExposures] = useState([]);
  const [assets, setAssets] = useState([]);
  const [services, setServices] = useState([]);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState(null);
  const [sortDir, setSortDir] = useState('asc');

  useEffect(() => {
    Promise.all([api.getExposures(), api.getAssets(), api.getBusinessServices()])
      .then(([exposureData, assetData, serviceData]) => {
        setExposures(exposureData);
        setAssets(assetData);
        setServices(serviceData);
      })
      .catch(setError);
  }, []);

  const lookup = useMemo(() => ({
    assets: Object.fromEntries(assets.map((asset) => [asset.id, asset])),
    services: Object.fromEntries(services.map((service) => [service.id, service])),
  }), [assets, services]);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const sorted = useMemo(() => {
    if (!sortKey) return exposures;
    return [...exposures].sort((a, b) => {
      const aVal = String(a[sortKey] || '').toLowerCase();
      const bVal = String(b[sortKey] || '').toLowerCase();
      return sortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
  }, [exposures, sortKey, sortDir]);

  const filtered = useMemo(() => {
    if (!search) return sorted;
    const q = search.toLowerCase();
    return sorted.filter((exposure) =>
      exposure.title.toLowerCase().includes(q) ||
      exposure.description.toLowerCase().includes(q) ||
      exposure.exposure_type.toLowerCase().includes(q) ||
      exposure.severity.toLowerCase().includes(q)
    );
  }, [sorted, search]);

  const exposureTypes = exposures.reduce((acc, exposure) => {
    acc[exposure.exposure_type] = (acc[exposure.exposure_type] || 0) + 1;
    return acc;
  }, {});

  if (error) return <div className="notice-panel error">Unable to load discovery data. {error.message}</div>;
  if (!exposures.length) return <DiscoveryLoading />;

  const sortIcon = (columnKey) => {
    if (sortKey !== columnKey) return <span className="sort-indicator">&#x2195;</span>;
    return <span className="sort-indicator active">{sortDir === 'asc' ? '&#x2191;' : '&#x2193;'}</span>;
  };

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Stage 2</p>
          <h1 className="page-title">Discovery</h1>
          <p className="page-intro">
            Normalize exposures across CVEs, cloud, identity, secrets, SaaS, and controls so leaders see paths, not just findings.
          </p>
        </div>
      </section>

      {api.isLiveMode() && (
        <CsvToolbar
          onExport={() => api.exportExposuresCsv()}
          onImport={(file) => api.importExposuresCsv(file)}
          label="Exposures"
        />
      )}

      <section className="metric-grid">
        {Object.entries(exposureTypes).map(([type, count]) => (
          <div className="metric-card compact" key={type}>
            <span>{type}</span>
            <strong>{count}</strong>
          </div>
        ))}
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Exposure Inventory</h2>
          <p>Discovery captures evidence and context needed for prioritization, not just severity.</p>
        </div>
        <TableSearch value={search} onChange={setSearch} placeholder="Search exposures..." />
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th className="sortable" onClick={() => handleSort('title')}>Exposure {sortIcon('title')}</th>
                <th className="sortable" onClick={() => handleSort('exposure_type')}>Type {sortIcon('exposure_type')}</th>
                <th>Asset</th>
                <th>Service</th>
                <th className="sortable" onClick={() => handleSort('severity')}>Severity {sortIcon('severity')}</th>
                <th>Threat signal</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((exposure) => {
                const asset = lookup.assets[exposure.asset_id];
                const service = lookup.services[asset?.service_id];
                return (
                  <tr key={exposure.id} className="clickable-row">
                    <td><strong>{exposure.title}</strong><span>{exposure.description}</span></td>
                    <td>{exposure.exposure_type}</td>
                    <td>{asset?.name}</td>
                    <td>{service?.name}</td>
                    <td><span className={`badge severity-${exposure.severity.toLowerCase()}`}>{exposure.severity}</span></td>
                    <td>
                      <span>
                        <Tooltip label="CISA Known Exploited Vulnerabilities catalog — confirmed active exploitation in the wild">
                          {exposure.kev_signal ? 'Known exploited' : 'No KEV signal'}
                        </Tooltip>
                      </span>
                      <span>
                        <Tooltip label="Exploit Prediction Scoring System — probability of exploitation within 30 days">
                          {Math.round(exposure.epss_probability * 100)}% EPSS
                        </Tooltip>
                      </span>
                    </td>
                    <td>{exposure.evidence_confidence}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <p className="table-footer">{filtered.length} of {exposures.length} exposures</p>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Discovery Lens</h2>
          <p>CTEM broadens the intake beyond patchable vulnerabilities.</p>
        </div>
        <div className="principle-grid">
          <div className="principle-card">CVE severity is captured, but it is only one signal in the exposure story.</div>
          <div className="principle-card">Identity and secrets are modeled because they often collapse control boundaries.</div>
          <div className="principle-card">Cloud reachability and segmentation turn static findings into attack-path evidence.</div>
          <div className="principle-card">Evidence confidence tells leaders whether to act, validate further, or track.</div>
        </div>
      </section>
    </div>
  );
};

export default Discovery;
