from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.dependencies import alpr_service


@asynccontextmanager
async def lifespan(_: FastAPI):
    alpr_service.load()
    yield
    alpr_service.unload()
