import os
import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger("tidyhome")

app = FastAPI(title="TidyHome", version="0.1.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>TidyHome</title>
        <style>
            body { font-family: sans-serif; display: flex; justify-content: center;
                   align-items: center; height: 100vh; margin: 0; background: #f0f4f8; }
            .card { background: white; padding: 2rem 3rem; border-radius: 1rem;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
            h1 { color: #3d7ab5; margin-bottom: 0.5rem; }
            p  { color: #666; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🧹 TidyHome</h1>
            <p>Add-on laeuft. Entwicklung in Arbeit.</p>
        </div>
    </body>
    </html>
    """


@app.get("/healthz")
async def health():
    return {"status": "ok", "version": "0.1.0"}


if __name__ == "__main__":
    logger.info("TidyHome API startet auf Port 8099")
    uvicorn.run(app, host="0.0.0.0", port=8099, log_level=log_level.lower())
