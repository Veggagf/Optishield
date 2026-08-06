from typing import Literal

from pydantic import BaseModel


class AlertStatusUpdate(BaseModel):
    estatus: Literal["nueva", "atendida", "descartada"]
