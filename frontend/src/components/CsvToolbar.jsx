import { useRef, useState } from 'react';
import { Download, FileDown, Upload, RotateCcw } from 'lucide-react';

import ConfirmDialog from './ConfirmDialog';
import { useToast } from './Toast';

const TEMPLATES = {
  Assets: ['name', 'type', 'service_id', 'owner', 'crown_jewel', 'reachable_from_internet'],
  Exposures: ['title', 'description', 'exposure_type', 'asset_id', 'severity', 'epss_probability', 'kev_signal', 'evidence_confidence', 'source', 'source_reference', 'last_seen', 'validated_at'],
  Remediation: ['title', 'playbook', 'owner', 'sla', 'status', 'priority', 'risk_acceptance_required'],
};

const StatusMessage = ({ status }) => {
  if (!status) return null;
  return (
    <p className={`csv-status ${status.type}`}>
      {status.type === 'success'
        ? `Imported ${status.imported} row${status.imported !== 1 ? 's' : ''}.`
        : status.type === 'error'
          ? status.errors
            ? `Import failed on ${status.errors.length} row${status.errors.length !== 1 ? 's' : ''}.`
            : status.message || 'Import failed.'
          : null}
    </p>
  );
};

const ErrorDetails = ({ errors }) => {
  if (!errors || errors.length === 0) return null;
  return (
    <div className="csv-errors">
      {errors.slice(0, 10).map((err, i) => (
        <p key={i} className="csv-error-line">
          Row {err.row}: <strong>{err.field}</strong> — {err.message}
        </p>
      ))}
      {errors.length > 10 && (
        <p className="csv-error-line muted">...and {errors.length - 10} more errors</p>
      )}
    </div>
  );
};

const CsvToolbar = ({
  onExport,
  onImport,
  onReset,
  label,
  acceptReset,
}) => {
  const fileRef = useRef(null);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const addToast = useToast();

  const handleExport = async () => {
    setBusy(true);
    setStatus(null);
    try {
      await onExport();
      addToast(`${label} exported successfully`, 'success');
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
      addToast(`Export failed: ${err.message}`, 'error');
    } finally {
      setBusy(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setStatus(null);
    try {
      const result = await onImport(file);
      if (result.errors?.length > 0) {
        setStatus({ type: 'error', errors: result.errors });
        addToast(`Import completed with ${result.errors.length} error(s)`, 'error');
      } else {
        setStatus({ type: 'success', imported: result.imported });
        addToast(`Imported ${result.imported} row(s)`, 'success');
      }
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
      addToast(`Import failed: ${err.message}`, 'error');
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const handleReset = async () => {
    setShowConfirm(false);
    setBusy(true);
    setStatus(null);
    try {
      await onReset();
      addToast('Data reset to seed values', 'success');
      window.location.reload();
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
      addToast(`Reset failed: ${err.message}`, 'error');
    } finally {
      setBusy(false);
    }
  };

  const handleTemplate = () => {
    const fields = TEMPLATES[label];
    if (!fields) return;
    const header = fields.join(',');
    const bom = '\uFEFF';
    const blob = new Blob([bom + header], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${label.toLowerCase()}-template.csv`;
    link.click();
    URL.revokeObjectURL(url);
    addToast('Template downloaded', 'success');
  };

  return (
    <div className="csv-toolbar">
      <div className="csv-toolbar-row">
        <button
          className="tool-button"
          type="button"
          onClick={handleExport}
          disabled={busy}
          aria-label={`Export ${label} to CSV`}
        >
          <Download size={16} />
          <span>Export {label}</span>
        </button>

        <button
          className="tool-button"
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={busy}
          aria-label={`Import ${label} from CSV`}
        >
          <Upload size={16} />
          <span>Import {label}</span>
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          style={{ display: 'none' }}
          onChange={handleFileChange}
          aria-hidden="true"
        />

        <button
          className="tool-button"
          type="button"
          onClick={handleTemplate}
          aria-label={`Download ${label} CSV template`}
        >
          <FileDown size={16} />
          <span>Template</span>
        </button>

        {acceptReset && (
          <button
            className="tool-button"
            type="button"
            onClick={() => setShowConfirm(true)}
            disabled={busy}
          >
            <RotateCcw size={16} />
            <span>Reset to seed</span>
          </button>
        )}
      </div>

      <StatusMessage status={status} />
      <ErrorDetails errors={status?.errors} />

      {showConfirm && (
        <ConfirmDialog
          message="Reset all data to seed values? This cannot be undone."
          onConfirm={handleReset}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  );
};

export default CsvToolbar;
