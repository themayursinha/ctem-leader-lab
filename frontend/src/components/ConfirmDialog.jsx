import { useEffect, useRef } from 'react';
import { AlertTriangle } from 'lucide-react';

const ConfirmDialog = ({ message, onConfirm, onCancel }) => {
  const confirmRef = useRef(null);

  useEffect(() => {
    confirmRef.current?.focus();
  }, []);

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') onCancel();
    if (e.key === 'Enter') onConfirm();
  };

  return (
    <div className="modal-overlay" onClick={onCancel} onKeyDown={handleKeyDown}>
      <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
        <AlertTriangle size={24} className="confirm-icon" />
        <p className="confirm-message">{message}</p>
        <div className="confirm-actions">
          <button className="tool-button" onClick={onCancel} autoFocus>
            Cancel
          </button>
          <button className="tool-button confirm-danger" onClick={onConfirm} ref={confirmRef}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
