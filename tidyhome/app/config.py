import os
import logging

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger("tidyhome")

# Admins aus der Add-on-Konfiguration – nur als Bootstrap beim ersten Start.
# Danach werden Admins in der App-UI verwaltet (TinyDB).
_raw = os.environ.get("ADMINS", "")
BOOTSTRAP_ADMINS: set[str] = {a.strip() for a in _raw.split(",") if a.strip()}
