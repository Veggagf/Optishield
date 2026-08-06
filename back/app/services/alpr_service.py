from app.core.config import settings
from app.services.alpr_engine import MotorALPR


class ALPRService:
    def __init__(self) -> None:
        self.motor: MotorALPR | None = None

    @property
    def loaded(self) -> bool:
        return self.motor is not None

    def load(self) -> None:
        if self.motor is not None:
            return

        self.motor = MotorALPR(settings.yolo_model_path)
        print(
            "Motor ALPR cargado correctamente desde: "
            f"{settings.yolo_model_path}"
        )

    def unload(self) -> None:
        self.motor = None

    def process_image(self, image):
        if self.motor is None:
            raise RuntimeError("El motor ALPR no está disponible.")

        return self.motor.process_image(image)
