from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import supabase_service
from app.schemas import WantedVehicleCreate

router = APIRouter(
    prefix="/api/wanted",
    tags=["Vehículos buscados"],
)


@router.post("")
def create_wanted_vehicle(data: WantedVehicleCreate):
    try:
        vehicle = supabase_service.create_wanted_vehicle(
            plate=data.placa,
            reason=data.motivo,
            priority=data.prioridad,
            color=data.color,
            model=data.modelo,
            brand=data.marca,
            year=data.anio,
            registered_by=data.registrado_por,
        )

        return {
            "success": True,
            "message": "Vehículo agregado a la lista de búsqueda.",
            "vehicle": vehicle,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error registrando vehículo: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


@router.get("")
def list_wanted(
    limit: int = Query(100, ge=1, le=500),
    active_only: bool = Query(True),
):
    try:
        return {
            "success": True,
            "vehicles": supabase_service.get_wanted_vehicles(
                limit=limit,
                active_only=active_only,
            ),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error consultando vehículos: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


@router.get("/{plate}")
def find_wanted(plate: str):
    try:
        normalized = supabase_service.normalize_plate(plate)
        vehicle = supabase_service.find_wanted_vehicle(
            normalized
        )

        return {
            "success": True,
            "plate": normalized,
            "wanted": vehicle is not None,
            "vehicle": vehicle,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error consultando matrícula: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error


@router.patch("/{vehicle_id}/deactivate")
def deactivate_wanted(vehicle_id: int):
    try:
        vehicle = supabase_service.deactivate_wanted_vehicle(
            vehicle_id
        )

        return {
            "success": True,
            "message": "La búsqueda fue desactivada.",
            "vehicle": vehicle,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error desactivando búsqueda: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error
