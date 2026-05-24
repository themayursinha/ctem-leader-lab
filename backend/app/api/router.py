from fastapi import APIRouter

from app.api.v1 import (
    assets,
    attack_paths,
    audit,
    auth,
    executive,
    exposures,
    program,
    remediation,
    sessions,
    workshop,
)

api_router = APIRouter()

api_router.include_router(program.router)
api_router.include_router(assets.router)
api_router.include_router(exposures.router)
api_router.include_router(remediation.router)
api_router.include_router(attack_paths.router)
api_router.include_router(workshop.router)
api_router.include_router(sessions.router)
api_router.include_router(audit.router)
api_router.include_router(executive.router)
api_router.include_router(auth.router)
