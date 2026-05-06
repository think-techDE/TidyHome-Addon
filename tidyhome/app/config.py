import os
import logging

log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger("tidyhome")

_admins_raw = os.environ.get("ADMINS", "")
ADMINS: set[str] = {a.strip() for a in _admins_raw.split(",") if a.strip()}
logger.info("Admins: %s", ADMINS or "(keine)")
