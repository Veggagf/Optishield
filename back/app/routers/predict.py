from fastapi import (
    APIRouter,
    File,
    HTTPException,
    Query,
    UploadFile,
)

from app.core.dependencies import alpr_service, supabase_service
from app.schemas import PredictionResponse
from app.services.image_service import decode_image, encode_image

router = APIRouter(
    prefix="/api/predict",
    tags=["Predicción"],
)


async def analyze_upload(
    file: UploadFile,
    register: bool,
    camera_id: str,
    location: str,
    origin: str,
) -> PredictionResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail="Solo se aceptan archivos de imagen.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="La imagen enviada está vacía.",
        )

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="La imagen no puede superar los 10 MB.",
        )

    image = decode_image(contents)

    try:
        annotated_image, detections = alpr_service.process_image(
            image
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Error procesando la imagen: "
                f"{type(error).__name__}: {error}"
            ),
        ) from error

    for detection in detections:
        try:
            wanted_vehicle = supabase_service.find_wanted_vehicle(
                detection["placa"]
            )
        except Exception as error:
            raise HTTPException(
                status_code=500,
                detail=(
                    "Error consultando vehículos buscados: "
                    f"{type(error).__name__}: {error}"
                ),
            ) from error

        detection["alerta"] = None

        if register:
            try:
                result = supabase_service.register_detection(
                    plate=detection["placa"],
                    confidence=detection["confianza"],
                    yolo_confidence=detection.get(
                        "confianza_yolo"
                    ),
                    ocr_confidence=detection.get(
                        "confianza_ocr"
                    ),
                    camera_id=camera_id,
                    location=location,
                    origin=origin,
                    wanted_vehicle=wanted_vehicle,
                )
            except Exception as error:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "La matrícula fue detectada, pero no "
                        "se pudo registrar: "
                        f"{type(error).__name__}: {error}"
                    ),
                ) from error

            if result["alert"]:
                detection["alerta"] = {
                    **result["alert"],
                    "vehiculo": wanted_vehicle,
                }

        elif wanted_vehicle:
            detection["alerta"] = {
                "estatus": "coincidencia_no_registrada",
                "vehiculo": wanted_vehicle,
            }

    message = (
        f"Se detectaron {len(detections)} matrícula(s)."
        if detections
        else "No se detectaron matrículas legibles."
    )

    return PredictionResponse(
        success=True,
        message=message,
        detections=detections,
        annotated_image=encode_image(annotated_image),
    )


@router.post(
    "/image",
    response_model=PredictionResponse,
)
async def predict_image(
    file: UploadFile = File(...),
    register: bool = Query(True),
):
    return await analyze_upload(
        file=file,
        register=register,
        camera_id="UPLOAD-01",
        location="Imagen cargada",
        origin="imagen",
    )


@router.post(
    "/frame",
    response_model=PredictionResponse,
)
async def predict_frame(
    file: UploadFile = File(...),
    register: bool = Query(True),
):
    return await analyze_upload(
        file=file,
        register=register,
        camera_id="WEB-CAM-01",
        location="Cámara del navegador",
        origin="camara",
    )
