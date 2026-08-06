from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import supabase_service

router = APIRouter(
    prefix="/api/detections",
    tags=["Detecciones"],
)


@router.get("")
def list_detections(
    limit: int = Query(50, ge=1, le=500),
):
    try:
        return {
            "success": True,
            "detections": supabase_service.get_detections(
                limit
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error consultando detecciones: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error
