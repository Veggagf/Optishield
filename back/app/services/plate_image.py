import cv2
import numpy as np


def crop_plate(
    image: np.ndarray,
    box: list[int],
) -> np.ndarray:
    image_height, image_width = image.shape[:2]
    x1, y1, x2, y2 = box

    margin_x = max(2, int((x2 - x1) * 0.04))
    margin_y = max(2, int((y2 - y1) * 0.08))

    crop_x1 = max(0, x1 - margin_x)
    crop_y1 = max(0, y1 - margin_y)
    crop_x2 = min(image_width, x2 + margin_x)
    crop_y2 = min(image_height, y2 + margin_y)

    return image[crop_y1:crop_y2, crop_x1:crop_x2]


def draw_detection(
    image: np.ndarray,
    box: list[int],
    plate: str,
    confidence: float,
) -> None:
    x1, y1, x2, y2 = box
    label = f"{plate} {confidence:.0%}"

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2,
    )

    cv2.putText(
        image,
        label,
        (x1, max(25, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
