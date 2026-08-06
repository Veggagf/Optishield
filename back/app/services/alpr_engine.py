from pathlib import Path
from typing import Any

import cv2
import easyocr
import numpy as np
from ultralytics import YOLO


class MotorALPR:
    def __init__(self, model_path: str) -> None:
        model_file = Path(model_path)

        if not model_file.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo YOLO en: {model_file.resolve()}"
            )

        self.detector = YOLO(str(model_file))
        self.reader = easyocr.Reader(["es", "en"], gpu=False)

    @staticmethod
    def clean_plate_text(text: str) -> str:
        return "".join(
            character
            for character in text.upper()
            if character.isalnum()
        )

    @staticmethod
    def preprocess_plate(plate_crop: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC,
        )

        return cv2.bilateralFilter(gray, 9, 75, 75)

    def process_ocr(
        self,
        plate_crop: np.ndarray,
    ) -> tuple[str, float]:
        if plate_crop.size == 0:
            return "", 0.0

        processed = self.preprocess_plate(plate_crop)

        readings = self.reader.readtext(
            processed,
            detail=1,
            paragraph=False,
        )

        accepted: list[tuple[str, float]] = []

        for _, text, confidence in readings:
            clean_text = self.clean_plate_text(text)

            if confidence >= 0.35 and clean_text:
                accepted.append(
                    (clean_text, float(confidence))
                )

        if not accepted:
            return "", 0.0

        plate_text = "".join(
            text
            for text, _ in accepted
        )

        average_confidence = sum(
            confidence
            for _, confidence in accepted
        ) / len(accepted)

        return plate_text, average_confidence

    def process_image(
        self,
        image: np.ndarray,
    ) -> tuple[np.ndarray, list[dict[str, Any]]]:
        annotated = image.copy()
        prediction = self.detector(image, verbose=False)[0]
        detections: list[dict[str, Any]] = []

        image_height, image_width = image.shape[:2]

        for box in prediction.boxes:
            yolo_confidence = float(box.conf[0])

            if yolo_confidence < 0.40:
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image_width, x2)
            y2 = min(image_height, y2)

            plate_crop = image[y1:y2, x1:x2]
            plate_text, ocr_confidence = self.process_ocr(
                plate_crop
            )

            if len(plate_text) < 4:
                continue

            final_confidence = min(
                yolo_confidence,
                ocr_confidence,
            )

            detections.append(
                {
                    "placa": plate_text,
                    "color": "No disponible",
                    "confianza": round(final_confidence, 4),
                    "confianza_yolo": round(yolo_confidence, 4),
                    "confianza_ocr": round(ocr_confidence, 4),
                    "box": [x1, y1, x2, y2],
                }
            )

            label = f"{plate_text} {final_confidence:.0%}"

            cv2.rectangle(
                annotated,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                annotated,
                label,
                (x1, max(25, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )

        return annotated, detections
