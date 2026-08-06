from pydantic import BaseModel, Field


class WantedVehicleCreate(BaseModel):
    placa: str = Field(min_length=1, max_length=20)
    motivo: str = Field(min_length=2, max_length=250)
    prioridad: int = Field(ge=1, le=3)
    color: str | None = Field(default=None, max_length=50)
    modelo: str | None = Field(default=None, max_length=100)
    marca: str | None = Field(default=None, max_length=100)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    registrado_por: str = Field(min_length=2, max_length=150)
