"""FastAPI 앱 진입점."""
import asyncio
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import seed
from app.routers import chat, games, survey

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174"
).split(",")

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed.run()  # 최초 실행 시에만 시딩 (데이터 없을 때)
    scheduler.add_job(seed.run_sync_force, "cron", hour=3, minute=0, id="daily_refresh")
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="Game Mod Compass API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(games.router)
app.include_router(survey.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
