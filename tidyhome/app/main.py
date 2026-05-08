import asyncio
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config import BOOTSTRAP_ADMINS, logger
from routes.dashboard import router as dashboard_router
from routes.projects import router as projects_router
from routes.scores import router as scores_router
from routes.settings import router as settings_router
from routes.tasks import router as tasks_router
from scheduler import scheduler_loop
from storage import PHOTO_DIR

APP_VERSION = "1.3.18"

app = FastAPI(title="TidyHome", version=APP_VERSION)

ASSETS_DIR = Path("/app/assets")
if not ASSETS_DIR.exists():
    ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
app.mount("/photos", StaticFiles(directory=PHOTO_DIR), name="photos")

app.include_router(dashboard_router)
app.include_router(tasks_router)
app.include_router(projects_router)
app.include_router(scores_router)
app.include_router(settings_router)


@app.on_event("startup")
async def _startup():
    from storage import get_admins, save_admins
    if not get_admins() and BOOTSTRAP_ADMINS:
        save_admins(list(BOOTSTRAP_ADMINS))
        logger.info("Admins aus Konfiguration geseedet: %s", BOOTSTRAP_ADMINS)
    elif not get_admins():
        logger.warning("Keine Admins konfiguriert – bitte in der App festlegen.")
    asyncio.create_task(scheduler_loop())


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": APP_VERSION}


if __name__ == "__main__":
    log_level = os.environ.get("LOG_LEVEL", "info").lower()
    ingress_path = os.environ.get("INGRESS_PATH", "")
    logger.info("TidyHome startet auf Port 8099 (ingress: %s)", ingress_path or "/")
    uvicorn.run(app, host="0.0.0.0", port=8099, root_path=ingress_path,
                log_level=log_level)
