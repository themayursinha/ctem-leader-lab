from fastapi import APIRouter, Depends

from app.dependencies import get_data_service
from app.models.domain import AttackPath
from app.services.data_service import DataService

router = APIRouter(tags=["Attack Paths"])


@router.get("/api/attack-paths", response_model=list[AttackPath])
def get_attack_paths(data: DataService = Depends(get_data_service)):
    return data.get_attack_paths()
