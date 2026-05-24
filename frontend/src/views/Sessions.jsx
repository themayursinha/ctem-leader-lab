import { useEffect, useState } from 'react';
import { History, KeyRound, Loader, Save, Trash2, Upload, FileText } from 'lucide-react';

import { api } from '../api';
import ConfirmDialog from '../components/ConfirmDialog';
import Skeleton from '../components/Skeleton';
import { useToast } from '../components/Toast';

const Sessions = () => {
  const [sessions, setSessions] = useState([]);
  const [auditEvents, setAuditEvents] = useState([]);
  const [adminToken, setAdminToken] = useState(api.getAdminToken());
  const [sessionName, setSessionName] = useState('');
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(null);
  const [deleting, setDeleting] = useState(null);
  const [message, setMessage] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [fetching, setFetching] = useState(true);
  const [auditError, setAuditError] = useState(null);
  const [error, setError] = useState(null);
  const addToast = useToast();

  const refreshSessions = () => {
    setFetching(true);
    api.listSessions().then((data) => {
      setSessions(data);
      setFetching(false);
    }).catch((err) => {
      setError(err);
      setFetching(false);
    });
  };

  const refreshAuditEvents = () => {
    api.listAuditEvents(50).then(setAuditEvents).catch(setAuditError);
  };

  useEffect(() => {
    api.listSessions().then((data) => {
      setSessions(data);
      setFetching(false);
    }).catch((err) => {
      setError(err);
      setFetching(false);
    });
    api.listAuditEvents(50).then(setAuditEvents).catch(setAuditError);
  }, []);

  const handleAdminTokenChange = (value) => {
    setAdminToken(value);
    api.setAdminToken(value);
  };

  const handleSave = async () => {
    const name = sessionName.trim();
    if (!name) return;
    setSaving(true);
    setMessage(null);
    try {
      await api.saveSession(name);
      setSessionName('');
      addToast(`Session "${name}" saved.`, 'success');
      refreshSessions();
      refreshAuditEvents();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
      addToast(err.message, 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleLoad = async (sessionId, sessionName) => {
    setLoading(sessionId);
    setMessage(null);
    try {
      await api.loadSession(sessionId);
      addToast(`Session "${sessionName}" loaded. Refreshing...`, 'success');
      window.setTimeout(() => window.location.reload(), 800);
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
      addToast(err.message, 'error');
      setLoading(null);
    }
  };

  const handleDelete = async () => {
    if (!confirmDelete) return;
    const { id, name } = confirmDelete;
    setConfirmDelete(null);
    setDeleting(id);
    setMessage(null);
    try {
      await api.deleteSession(id);
      addToast(`Session "${name}" deleted.`, 'success');
      refreshSessions();
      refreshAuditEvents();
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
      addToast(err.message, 'error');
    } finally {
      setDeleting(null);
    }
  };

  const handleSummary = async () => {
    setMessage(null);
    try {
      const blob = await api.getExecutiveSummary('markdown');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'ctem-executive-summary.md';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      addToast('Executive summary downloaded', 'success');
    } catch (err) {
      setMessage({ type: 'error', text: err.message });
      addToast(err.message, 'error');
    }
  };

  if (!api.isLiveMode()) {
    return (
      <div className="notice-panel">
        Sessions are only available when connected to a live backend. Start the API server with <code>VITE_API_BASE_URL</code> set.
      </div>
    );
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <p className="eyebrow">Workshop Sessions</p>
          <h1 className="page-title">Workshop Sessions</h1>
          <p className="page-intro">
            Save, load, and manage CTEM workshop snapshots. Each session captures the current state of assets, exposures, and remediation actions.
          </p>
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Admin Token</h2>
          <p>Required only when the backend is started with <code>CTEM_ADMIN_TOKEN</code>. Stored for this browser tab only.</p>
        </div>
        <div className="session-save-row">
          <input
            className="session-input"
            type="password"
            placeholder="Enter local admin token"
            value={adminToken}
            onChange={(e) => handleAdminTokenChange(e.target.value)}
            aria-label="Local admin token"
          />
          <button className="tool-button" type="button" onClick={() => handleAdminTokenChange('')} disabled={!adminToken}>
            <KeyRound size={16} />
            <span>Clear Token</span>
          </button>
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Save Current Session</h2>
          <p>Name the current workshop state so it can be restored later.</p>
        </div>
        <div className="session-save-row">
          <input
            className="session-input"
            type="text"
            placeholder="e.g. Sprint 12 review, pre-audit baseline"
            value={sessionName}
            onChange={(e) => setSessionName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
            disabled={saving}
          />
          <button
            className="tool-button"
            type="button"
            onClick={handleSave}
            disabled={saving || !sessionName.trim()}
            aria-label="Save current session"
          >
            {saving ? <Loader size={16} className="spin" /> : <Save size={16} />}
            <span>{saving ? 'Saving...' : 'Save Session'}</span>
          </button>
        </div>
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Saved Sessions</h2>
          <p>Click Load to restore a session. All current views will refresh.</p>
        </div>
        {fetching ? (
          <div className="notice-panel"><Skeleton width="100%" height="6rem" /></div>
        ) : error ? (
          <div className="notice-panel error">Unable to load sessions. {error.message}</div>
        ) : sessions.length === 0 ? (
          <div className="notice-panel">No saved sessions yet.</div>
        ) : (
          <div className="table-wrap">
            <table className="data-table" aria-label="Saved workshop sessions">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Created</th>
                  <th>Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td><strong>{session.name}</strong></td>
                    <td>{new Date(session.created_at).toLocaleString()}</td>
                    <td>{new Date(session.updated_at).toLocaleString()}</td>
                    <td>
                      <div className="session-actions">
                        <button
                          className="tool-button compact"
                          type="button"
                          onClick={() => handleLoad(session.id, session.name)}
                          disabled={loading === session.id}
                          aria-label={`Load session "${session.name}"`}
                        >
                          {loading === session.id ? <Loader size={14} className="spin" /> : <Upload size={14} />}
                          <span>Load</span>
                        </button>
                        <button
                          className="tool-button compact danger"
                          type="button"
                          onClick={() => setConfirmDelete({ id: session.id, name: session.name })}
                          disabled={deleting === session.id}
                          aria-label={`Delete session "${session.name}"`}
                        >
                          <Trash2 size={14} />
                          <span>Delete</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>


      <section className="content-section">
        <div className="section-heading">
          <h2><History size={18} aria-hidden="true" /> Audit Events</h2>
          <p>Recent state-changing actions recorded by the live backend.</p>
        </div>
        {auditError ? (
          <div className="notice-panel error">Unable to load audit events. {auditError.message}</div>
        ) : auditEvents.length === 0 ? (
          <div className="notice-panel">No audit events recorded yet.</div>
        ) : (
          <div className="table-wrap">
            <table className="data-table" aria-label="Audit events">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>Summary</th>
                </tr>
              </thead>
              <tbody>
                {auditEvents.map((event) => (
                  <tr key={event.id}>
                    <td>{new Date(event.created_at).toLocaleString()}</td>
                    <td><strong>{event.action}</strong></td>
                    <td>{event.resource_type}{event.resource_id ? ` / ${event.resource_id}` : ''}</td>
                    <td>{event.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="content-section">
        <div className="section-heading">
          <h2>Executive Summary</h2>
          <p>Download a formatted Markdown report of the current CTEM program state.</p>
        </div>
        <button className="tool-button" type="button" onClick={handleSummary}>
          <FileText size={16} />
          <span>Download Executive Summary</span>
        </button>
      </section>

      {message && (
        <div className={`session-message ${message.type}`}>
          {message.text}
        </div>
      )}

      {confirmDelete && (
        <ConfirmDialog
          message={`Delete session "${confirmDelete.name}"? This cannot be undone.`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(null)}
        />
      )}
    </div>
  );
};

export default Sessions;
