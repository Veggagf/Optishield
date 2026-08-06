from datetime import datetime, timezone
from typing import Any
from supabase import Client, create_client
from app.core.config import settings


class SupabaseService:
    def __init__(self) -> None:
        self.client: Client | None = (
            create_client(
                settings.supabase_url,
                settings.supabase_key,
            )
            if settings.supabase_url and settings.supabase_key
            else None
        )

    @property
    def connected(self) -> bool:
        return self.client is not None

    def _require_client(self) -> Client:
        if self.client is None:
            raise RuntimeError("Supabase no está configurado correctamente.")

        return self.client

    @staticmethod
    def normalize_plate(plate: str) -> str:
        return "".join(character for character in plate.upper() if character.isalnum())

    def create_wanted_vehicle(
        self,
        plate: str,
        reason: str,
        priority: int,
        registered_by: str,
        color: str | None = None,
        model: str | None = None,
        brand: str | None = None,
        year: int | None = None,
    ) -> dict[str, Any]:
        client = self._require_client()
        normalized_plate = self.normalize_plate(plate)

        existing = (
            client.table(settings.wanted_table)
            .select("id, placa")
            .eq("placa", normalized_plate)
            .eq("activo", True)
            .limit(1)
            .execute()
        )

        if existing.data:
            raise ValueError(
                f"La matrícula {normalized_plate} ya está en búsqueda activa."
            )

        payload = {
            "placa": normalized_plate,
            "motivo": reason.strip(),
            "prioridad": priority,
            "color": color.strip() if color else None,
            "modelo": model.strip() if model else None,
            "marca": brand.strip() if brand else None,
            "anio": year,
            "registrado_por": registered_by.strip(),
            "activo": True,
        }

        response = client.table(settings.wanted_table).insert(payload).execute()

        if not response.data:
            raise RuntimeError("Supabase no devolvió el vehículo registrado.")

        return response.data[0]

    def get_wanted_vehicles(
        self,
        limit: int = 100,
        active_only: bool = True,
    ) -> list[dict[str, Any]]:
        client = self._require_client()

        query = (
            client.table(settings.wanted_table)
            .select("*")
            .order("prioridad", desc=True)
            .order("creado_en", desc=True)
            .limit(limit)
        )

        if active_only:
            query = query.eq("activo", True)

        response = query.execute()
        return response.data or []

    def find_wanted_vehicle(
        self,
        plate: str,
    ) -> dict[str, Any] | None:
        client = self._require_client()
        normalized_plate = self.normalize_plate(plate)

        response = (
            client.table(settings.wanted_table)
            .select("*")
            .eq("placa", normalized_plate)
            .eq("activo", True)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None

    def deactivate_wanted_vehicle(
        self,
        vehicle_id: int,
    ) -> dict[str, Any]:
        client = self._require_client()

        response = (
            client.table(settings.wanted_table)
            .update({"activo": False})
            .eq("id", vehicle_id)
            .execute()
        )

        if not response.data:
            raise ValueError("No se encontró el vehículo buscado.")

        return response.data[0]

    def register_detection(
        self,
        plate: str,
        confidence: float,
        yolo_confidence: float | None,
        ocr_confidence: float | None,
        camera_id: str,
        location: str,
        origin: str,
        wanted_vehicle: dict[str, Any] | None,
    ) -> dict[str, Any]:
        client = self._require_client()

        payload = {
            "placa": self.normalize_plate(plate),
            "fecha_hora": datetime.now(timezone.utc).isoformat(),
            "confianza": round(float(confidence), 4),
            "confianza_yolo": (
                round(float(yolo_confidence), 4)
                if yolo_confidence is not None
                else None
            ),
            "confianza_ocr": (
                round(float(ocr_confidence), 4) if ocr_confidence is not None else None
            ),
            "camara_id": camera_id,
            "ubicacion": location,
            "origen": origin,
            "vehiculo_buscado_id": (
                wanted_vehicle.get("id") if wanted_vehicle else None
            ),
            "tiene_alerta": wanted_vehicle is not None,
        }

        response = client.table(settings.detections_table).insert(payload).execute()

        if not response.data:
            raise RuntimeError("Supabase no devolvió la detección registrada.")

        detection = response.data[0]
        alert = None

        if wanted_vehicle:
            alert = self.create_alert(
                detection_id=detection["id"],
                wanted_vehicle_id=wanted_vehicle["id"],
            )

        return {
            "detection": detection,
            "alert": alert,
        }

    def create_alert(
        self,
        detection_id: int,
        wanted_vehicle_id: int,
    ) -> dict[str, Any]:
        client = self._require_client()

        response = (
            client.table(settings.alerts_table)
            .insert(
                {
                    "deteccion_id": detection_id,
                    "vehiculo_buscado_id": wanted_vehicle_id,
                    "estatus": "nueva",
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError("Supabase no devolvió la alerta creada.")

        return response.data[0]

    def get_detections(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        client = self._require_client()

        response = (
            client.table(settings.detections_table)
            .select("*")
            .order("fecha_hora", desc=True)
            .limit(limit)
            .execute()
        )

        return response.data or []

    def get_alerts(
        self,
        limit: int = 50,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        client = self._require_client()

        query = (
            client.table(settings.alerts_table)
            .select("*, detecciones(*), vehiculos_buscados(*)")
            .order("fecha_alerta", desc=True)
            .limit(limit)
        )

        if status:
            query = query.eq("estatus", status)

        response = query.execute()
        return response.data or []

    def update_alert_status(
        self,
        alert_id: int,
        status: str,
    ) -> dict[str, Any]:
        client = self._require_client()

        response = (
            client.table(settings.alerts_table)
            .update({"estatus": status})
            .eq("id", alert_id)
            .execute()
        )

        if not response.data:
            raise ValueError("No se encontró la alerta.")

        return response.data[0]
