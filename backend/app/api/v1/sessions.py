from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import require_admin_token
from app.dependencies import get_data_service
from app.services.data_service import DataService

router = APIRouter(tags=["Sessions"])


@router.post("/api/sessions", dependencies=[Depends(require_admin_token)])
def create_session(name: str = Query(..., min_length=1, max_length=200),
                   data: DataService = Depends(get_data_service)):
    clean_name = name.strip()
    session_id = data.save_session(name=clean_name)
    data.record_audit_event(
        "save_session", "session", session_id, f'Saved session "{clean_name}".', {"name": clean_name}
    )
    return {"id": session_id, "name": clean_name}


@router.get("/api/sessions")
def list_sessions(data: DataService = Depends(get_data_service)):
    return data.list_sessions()


@router.get("/api/sessions/{session_id}")
def get_session(session_id: str, data: DataService = Depends(get_data_service)):
    info = data.get_session_info(session_id)
    if info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return info


@router.post("/api/sessions/{session_id}/load", dependencies=[Depends(require_admin_token)])
def load_session(session_id: str, data: DataService = Depends(get_data_service)):
    ok = data.load_session(session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    data.record_audit_event("load_session", "session", session_id, f"Loaded session {session_id}.", {})
    return {"status": f"Session {session_id} loaded"}


@router.delete("/api/sessions/{session_id}", dependencies=[Depends(require_admin_token)])
def delete_session(session_id: str, data: DataService = Depends(get_data_service)):
    ok = data.delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    data.record_audit_event("delete_session", "session", session_id, f"Deleted session {session_id}.", {})
    return {"status": f"Session {session_id} deleted"}
