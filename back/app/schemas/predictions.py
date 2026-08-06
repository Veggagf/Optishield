from typing import Any

from pydantic import BaseModel, Field


class DetectionResult(BaseModel):
    placa: str
    color: str
    confianza: float = Field(ge=0, le=1)
    confianza_yolo: float = Field(ge=0, le=1)
    confianza_ocr: float = Field(ge=0, le=1)
    box: list[int]
    alerta: dict[str, Any] | None = None


class PredictionResponse(BaseModel):
    success: bool
    message: str
    detections: list[DetectionResult]
    annotated_image: str | None = None
