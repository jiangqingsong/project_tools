from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.router import register_routers
from app.core.file_utils import start_cleanup_scheduler, stop_cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_cleanup_scheduler()
    yield
    stop_cleanup_scheduler()


app = FastAPI(title="Project Tools", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_routers(app)
