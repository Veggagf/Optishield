from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import supabase_service
from app.schemas import AlertStatusUpdate

router = APIRouter(
    prefix="/api/alerts",
    tags=["Alertas"],
)


@router.get("")
def list_alerts(
    limit: int = Query(50, ge=1, le=500),
    status: str | None = Query(None),
):
    try:
        return {
            "success": True,
            "alerts": supabase_service.get_alerts(
                limit=limit,
                status=status,
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error consultando alertas: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


@router.patch("/{alert_id}")
def update_alert(
    alert_id: int,
    data: AlertStatusUpdate,
):
    try:
        alert = supabase_service.update_alert_status(
            alert_id=alert_id,
            status=data.estatus,
        )

        return {
            "success": True,
            "message": "Estatus de alerta actualizado.",
            "alert": alert,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error actualizando alerta: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error
