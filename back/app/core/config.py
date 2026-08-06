import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    supabase_url: str = os.getenv("SUPABASE_URL", "").strip()
    supabase_key: str = os.getenv("SUPABASE_KEY", "").strip()

    wanted_table: str = os.getenv(
        "SUPABASE_WANTED_TABLE",
        "vehiculos_buscados",
    )
    detections_table: str = os.getenv(
        "SUPABASE_DETECTIONS_TABLE",
        "detecciones",
    )
    alerts_table: str = os.getenv(
        "SUPABASE_ALERTS_TABLE",
        "alertas",
    )

    yolo_model_path: str = os.getenv(
        "YOLO_MODEL_PATH",
        "models/best.pt",
    )

    allowed_origins: list[str] = field(
        default_factory=lambda: [
            origin.strip()
            for origin in os.getenv(
                "ALLOWED_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173",
            ).split(",")
            if origin.strip()
        ]
    )


settings = Settings()
