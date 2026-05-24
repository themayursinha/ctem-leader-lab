import { useEffect, useMemo, useState } from 'react'

import { api } from '../api'
import CsvToolbar from '../components/CsvToolbar'
import Skeleton from '../components/Skeleton'
import TableSearch from '../components/TableSearch'
import Tooltip from '../components/Tooltip'
import type { Asset, BusinessService, WorkshopArtifacts } from '../types/api'

const ScopingLoading = () => (
  <div className="page-stack">
    <section className="page-header">
      <Skeleton width="80px" height="0.75rem" />
      <Skeleton width="200px" height="2rem" margin="4px 0 0" />
      <Skeleton width="100%" height="1rem" margin="12px 0 0" />
    </section>
    <section className="service-grid">
      {[1, 2, 3].map((i) => (
        <div className="service-card" key={i}>
          <Skeleton width="120px" height="0.85rem" />
          <Skeleton width="160px" height="1.1rem" margin="8px 0 0" />
          <Skeleton width="100%" height="0.85rem" margin="12px 0 0" />
          <Skeleton width="100%" height="4rem" margin="12px 0 0" />
        </div>
      ))}
    </section>
  </div>
)

const Scoping = () => {
  const [services, setServices] = useState<BusinessService[]>([])
  const [assets, setAssets] = useState<Asset[]>([])
  const [artifacts, setArtifacts] = useState<WorkshopArtifacts | null>(null)
  const [error, setError] = useState<Error | null>(null)
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  useEffect(() => {
    Promise.all([api.getBusinessServices(), api.getAssets(), api.getWorkshopArtifacts()])
      .then(([serviceData, assetData, artifactData]) => {
        setServices(serviceData)
        setAssets(assetData)
        setArtifacts(artifactData)
      })
      .catch(setError)
  }, [])

  const assetsById = useMemo(() => Object.fromEntries(assets.map((asset) => [asset.id, asset])), [assets])
  const serviceMap = useMemo(() => Object.fromEntries(services.map((s) => [s.id, s.name])), [services])

  const sorted = useMemo(() => {
    if (!sortKey) return assets
    return [...assets].sort((a, b) => {
      const aVal = String((a as unknown as Record<string, unknown>)[sortKey] || '').toLowerCase()
      const bVal = String((b as unknown as Record<string, unknown>)[sortKey] || '').toLowerCase()
      return sortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    })
  }, [assets, sortKey, sortDir])

  const filtered = useMemo(() => {
    if (!search) return sorted
    const q = search.toLowerCase()
    return sorted.filter((asset) =>
      asset.name.toLowerCase().includes(q) ||
      asset.type.toLowerCase().includes(q) ||
      asset.owner.toLowerCase().includes(q)
    )
  }, [sorted, search])

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  if (error) return <div className="notice-panel error"><strong>Unable to load scoping data.</strong> The backend may be unavailable.<div className="error-detail">{error.message}</div></div>
  if (!artifacts) return <ScopingLoading />

  const sortIcon = (columnKey: string) => {
    if (sortKey !== columnKey) return <span className="sort-indicator">&#x2195;</span>
    return <span className="sort-indicator active">{sortDir === 'asc' ? '&#x2191;' : '&#x2193;'}</span>
  }

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

      {api.isLiveMode() ? (
        <CsvToolbar
          onExport={() => api.exportAssetsCsv()}
          onImport={(file) => api.importAssetsCsv(file)}
          label="Assets"
          acceptReset={false}
        />
      ) : (
        <div className="static-notice">CSV import and export require a live backend. Start the API server to unlock these features.</div>
      )}

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
        <TableSearch value={search} onChange={setSearch} placeholder="Search assets..." />
        <div className="table-wrap">
          <table className="data-table" aria-label="Asset inventory">
            <thead>
              <tr>
                  <th className="sortable" onClick={() => handleSort('name')} aria-sort={sortKey === 'name' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}>Asset {sortIcon('name')}</th>
                <th>Service</th>
                <th className="sortable" onClick={() => handleSort('owner')} aria-sort={sortKey === 'owner' ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}>Owner {sortIcon('owner')}</th>
                <th>Exposure</th>
                <th><Tooltip label="An asset so critical to the business that its compromise would cause significant operational or reputational harm">Crown jewel</Tooltip></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((asset) => (
                <tr key={asset.id} className="clickable-row">
                  <td><strong>{asset.name}</strong><span>{asset.type}</span></td>
                  <td>{serviceMap[asset.service_id]}</td>
                  <td>{asset.owner}</td>
                  <td><Tooltip label="Whether this asset is reachable from the public internet">{asset.reachable_from_internet}</Tooltip></td>
                  <td>{asset.crown_jewel ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="table-footer">{filtered.length} of {assets.length} assets</p>
      </section>
    </div>
  )
}

export default Scoping
