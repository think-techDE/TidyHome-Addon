import asyncio
import os

import uvicorn
from fastapi import FastAPI

from config import logger
from routes.dashboard import router as dashboard_router
from routes.projects import router as projects_router
from routes.scores import router as scores_router
from routes.settings import router as settings_router
from routes.tasks import router as tasks_router
from scheduler import scheduler_loop

app = FastAPI(title="TidyHome", version="1.0.0")

app.include_router(dashboard_router)
app.include_router(tasks_router)
app.include_router(projects_router)
app.include_router(scores_router)
app.include_router(settings_router)


@app.on_event("startup")
async def _start_scheduler():
    asyncio.create_task(scheduler_loop())


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    ingress_path = os.environ.get("INGRESS_PATH", "")
    logger.info("TidyHome startet auf Port 8099 (ingress: %s)", ingress_path or "/")
    uvicorn.run(app, host="0.0.0.0", port=8099, root_path=ingress_path,
                log_level=log_level)
