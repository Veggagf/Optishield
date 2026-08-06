import base64

import cv2
import numpy as np
from fastapi import HTTPException


def decode_image(contents: bytes) -> np.ndarray:
    image_buffer = np.frombuffer(
        contents,
        dtype=np.uint8,
    )

    image = cv2.imdecode(
        image_buffer,
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise HTTPException(
            status_code=400,
            detail="El archivo enviado no es una imagen válida.",
        )

    return image


def encode_image(image: np.ndarray) -> str:
    success, image_buffer = cv2.imencode(
        ".jpg",
        image,
    )

    if not success:
        raise HTTPException(
            status_code=500,
            detail="No fue posible codificar la imagen procesada.",
        )

    encoded_image = base64.b64encode(
        image_buffer
    ).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded_image}"
