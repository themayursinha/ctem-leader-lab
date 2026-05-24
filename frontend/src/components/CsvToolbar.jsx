import { useRef, useState } from 'react';
import { Download, Upload, RotateCcw } from 'lucide-react';

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

  const handleExport = async () => {
    setBusy(true);
    setStatus(null);
    try {
      await onExport();
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
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
      } else {
        setStatus({ type: 'success', imported: result.imported });
      }
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setBusy(false);
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset all data to seed values? This cannot be undone.')) return;
    setBusy(true);
    setStatus(null);
    try {
      await onReset();
      window.location.reload();
    } catch (err) {
      setStatus({ type: 'error', message: err.message });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="csv-toolbar">
      <div className="csv-toolbar-row">
        <button
          className="tool-button"
          type="button"
          onClick={handleExport}
          disabled={busy}
        >
          <Download size={16} />
          <span>Export {label}</span>
        </button>

        <button
          className="tool-button"
          type="button"
          onClick={() => fileRef.current?.click()}
          disabled={busy}
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
        />

        {acceptReset && (
          <button
            className="tool-button"
            type="button"
            onClick={handleReset}
            disabled={busy}
          >
            <RotateCcw size={16} />
            <span>Reset to seed</span>
          </button>
        )}
      </div>

      <StatusMessage status={status} />
      <ErrorDetails errors={status?.errors} />
    </div>
  );
};

export default CsvToolbar;
