from fastapi import APIRouter

from app.core.dependencies import alpr_service, supabase_service

router = APIRouter(tags=["Sistema"])


@router.get("/")
def root():
    return {
        "name": "OptiShield ALPR API",
        "status": "online",
        "docs": "/docs",
        "model_loaded": alpr_service.loaded,
        "supabase_connected": supabase_service.connected,
    }


@router.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": alpr_service.loaded,
        "supabase_connected": supabase_service.connected,
    }
