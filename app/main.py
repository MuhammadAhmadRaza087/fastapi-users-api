from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import __version__
from app.config import SEED_ON_STARTUP
from app.database import init_db
from app.routers import health, users
from app.seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if SEED_ON_STARTUP:
        seed_if_empty()
    yield


app = FastAPI(
    title="Users API",
    description="Simple FastAPI CRUD for dummy users, with a health check.",
    version=__version__,
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(users.router)


@app.get("/", tags=["meta"])
def root():
    return {"service": "users-api", "version": __version__, "docs": "/docs", "health": "/health"}
