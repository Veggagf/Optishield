from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.routers import alerts, detections, health, predict, wanted


app = FastAPI(
    title="OptiShield ALPR API",
    version="2.0.0",
    description=(
        "API modular para reconocimiento de matrículas, "
        "vehículos buscados, detecciones y alertas."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(wanted.router)
app.include_router(detections.router)
app.include_router(alerts.router)
