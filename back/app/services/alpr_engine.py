from typing import Any

import numpy as np

from app.services.onnx_detector import ONNXPlateDetector
from app.services.plate_image import crop_plate, draw_detection
from app.services.plate_ocr import PlateOCR


class MotorALPR:
    """
    Coordina la detección ONNX y la lectura OCR.

    Esta versión incluye mensajes de depuración para identificar
    si el problema está en ONNX o en Tesseract.
    """

    def __init__(self, model_path: str) -> None:
        self.detector = ONNXPlateDetector(
            model_path=model_path,
            confidence_threshold=0.20,
            nms_threshold=0.45,
        )

        self.ocr = PlateOCR()

    def process_image(
        self,
        image: np.ndarray,
    ) -> tuple[np.ndarray, list[dict[str, Any]]]:
        annotated = image.copy()
        final_detections: list[dict[str, Any]] = []

        model_detections = self.detector.detect(image)

        print(f"[ALPR] ONNX encontró " f"{len(model_detections)} candidato(s)")

        for index, detected_plate in enumerate(
            model_detections,
            start=1,
        ):
            box = detected_plate["box"]
            yolo_confidence = float(detected_plate["confidence"])

            print(
                f"[ALPR] Candidato {index}: "
                f"box={box}, "
                f"confianza_yolo={yolo_confidence:.4f}"
            )

            plate_crop = crop_plate(
                image=image,
                box=box,
            )

            if plate_crop.size == 0:
                print(f"[ALPR] Candidato {index} descartado: " "el recorte está vacío.")
                continue

            print(f"[ALPR] Tamaño del recorte {index}: " f"{plate_crop.shape}")

            plate_text, ocr_confidence = self.ocr.read(plate_crop)

            print(
                f"[ALPR] Resultado OCR {index}: "
                f"texto='{plate_text}', "
                f"confianza_ocr={ocr_confidence:.4f}"
            )

            if len(plate_text) < 4:
                print(
                    f"[ALPR] Candidato {index}: "
                    "ONNX detectó la matrícula, "
                    "pero Tesseract no pudo leerla."
                )

                plate_text = "NOLEIDA"
                ocr_confidence = 0.0

            final_confidence = min(
                yolo_confidence,
                ocr_confidence,
            )

            detection = {
                "placa": plate_text,
                "color": "No disponible",
                "confianza": round(
                    final_confidence,
                    4,
                ),
                "confianza_yolo": round(
                    yolo_confidence,
                    4,
                ),
                "confianza_ocr": round(
                    ocr_confidence,
                    4,
                ),
                "box": box,
            }

            final_detections.append(detection)

            draw_detection(
                image=annotated,
                box=box,
                plate=plate_text,
                confidence=final_confidence,
            )

        print(f"[ALPR] Resultado final: " f"{len(final_detections)} detección(es)")

        return annotated, final_detections
