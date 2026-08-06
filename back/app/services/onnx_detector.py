from pathlib import Path
from typing import Any

import cv2
import numpy as np
import onnxruntime as ort


class ONNXPlateDetector:
    def __init__(
        self,
        model_path: str,
        confidence_threshold: float = 0.40,
        nms_threshold: float = 0.45,
    ) -> None:
        model_file = Path(model_path)

        if not model_file.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo ONNX en: {model_file.resolve()}"
            )

        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold

        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1

        self.session = ort.InferenceSession(
            str(model_file),
            sess_options=options,
            providers=["CPUExecutionProvider"],
        )

        model_input = self.session.get_inputs()[0]
        self.input_name = model_input.name
        self.input_height = int(model_input.shape[2])
        self.input_width = int(model_input.shape[3])

    @staticmethod
    def _letterbox(
        image: np.ndarray,
        target_width: int,
        target_height: int,
    ) -> tuple[np.ndarray, float, int, int]:
        original_height, original_width = image.shape[:2]

        scale = min(
            target_width / original_width,
            target_height / original_height,
        )

        resized_width = int(round(original_width * scale))
        resized_height = int(round(original_height * scale))

        resized = cv2.resize(
            image,
            (resized_width, resized_height),
            interpolation=cv2.INTER_LINEAR,
        )

        padding_x = target_width - resized_width
        padding_y = target_height - resized_height

        left = padding_x // 2
        right = padding_x - left
        top = padding_y // 2
        bottom = padding_y - top

        padded = cv2.copyMakeBorder(
            resized,
            top,
            bottom,
            left,
            right,
            cv2.BORDER_CONSTANT,
            value=(114, 114, 114),
        )

        return padded, scale, left, top

    def _preprocess(
        self,
        image: np.ndarray,
    ) -> tuple[np.ndarray, float, int, int]:
        padded, scale, padding_x, padding_y = self._letterbox(
            image,
            self.input_width,
            self.input_height,
        )

        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        tensor = rgb.astype(np.float32) / 255.0
        tensor = np.transpose(tensor, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)

        return np.ascontiguousarray(tensor), scale, padding_x, padding_y

    def _decode(
        self,
        output: np.ndarray,
        scale: float,
        padding_x: int,
        padding_y: int,
        original_width: int,
        original_height: int,
    ) -> list[dict[str, Any]]:
        predictions = np.squeeze(output, axis=0)

        if predictions.shape[0] == 5:
            predictions = predictions.T

        boxes_xywh: list[list[int]] = []
        scores: list[float] = []

        for prediction in predictions:
            center_x, center_y, width, height, confidence = prediction[:5]
            confidence = float(confidence)

            if confidence < self.confidence_threshold:
                continue

            x1 = int(round((float(center_x - width / 2) - padding_x) / scale))
            y1 = int(round((float(center_y - height / 2) - padding_y) / scale))
            box_width = int(round(float(width) / scale))
            box_height = int(round(float(height) / scale))

            x1 = max(0, min(x1, original_width - 1))
            y1 = max(0, min(y1, original_height - 1))
            box_width = max(1, min(box_width, original_width - x1))
            box_height = max(1, min(box_height, original_height - y1))

            boxes_xywh.append([x1, y1, box_width, box_height])
            scores.append(confidence)

        if not boxes_xywh:
            return []

        selected = cv2.dnn.NMSBoxes(
            boxes_xywh,
            scores,
            self.confidence_threshold,
            self.nms_threshold,
        )

        if len(selected) == 0:
            return []

        detections: list[dict[str, Any]] = []

        for index in np.array(selected).flatten():
            x1, y1, width, height = boxes_xywh[int(index)]

            detections.append(
                {
                    "box": [x1, y1, x1 + width, y1 + height],
                    "confidence": float(scores[int(index)]),
                }
            )

        return detections

    def detect(self, image: np.ndarray) -> list[dict[str, Any]]:
        original_height, original_width = image.shape[:2]
        tensor, scale, padding_x, padding_y = self._preprocess(image)

        output = self.session.run(
            None,
            {self.input_name: tensor},
        )[0]

        return self._decode(
            output=output,
            scale=scale,
            padding_x=padding_x,
            padding_y=padding_y,
            original_width=original_width,
            original_height=original_height,
        )
