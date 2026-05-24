from fastapi import APIRouter, Depends

from app.dependencies import get_data_service
from app.models.domain import WorkshopArtifacts
from app.services.data_service import DataService

router = APIRouter(tags=["Workshop"])


@router.get("/api/workshop-artifacts", response_model=WorkshopArtifacts)
def get_workshop_artifacts(data: DataService = Depends(get_data_service)):
    return data.get_workshop_artifacts()
