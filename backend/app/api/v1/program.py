from fastapi import APIRouter, Depends

from app.dependencies import get_data_service
from app.models.domain import BusinessService, MaturityDomain, ProgramSummary
from app.services.data_service import DataService

router = APIRouter(tags=["Program"])


@router.get("/api/program-summary", response_model=ProgramSummary)
def get_program_summary(data: DataService = Depends(get_data_service)):
    return data.get_program_summary()


@router.get("/api/business-services", response_model=list[BusinessService])
def get_business_services(data: DataService = Depends(get_data_service)):
    return data.get_business_services()


@router.get("/api/maturity", response_model=list[MaturityDomain])
def get_maturity(data: DataService = Depends(get_data_service)):
    return data.get_maturity()
