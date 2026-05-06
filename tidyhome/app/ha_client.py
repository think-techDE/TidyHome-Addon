import os
import aiohttp
import logging

logger = logging.getLogger("tidyhome.ha")

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
HA_BASE = "http://supervisor/core/api"


async def _get(path: str) -> dict | list | None:
    if not SUPERVISOR_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{HA_BASE}{path}", headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as r:
                if r.status == 200:
                    return await r.json()
    except Exception as e:
        logger.warning(f"HA API error {path}: {e}")
    return None


async def get_areas() -> list[str]:
    data = await _get("/config/area_registry/list")
    if not data:
        return _default_rooms()
    return sorted([a["name"] for a in data])


async def get_persons() -> list[str]:
    data = await _get("/states")
    if not data:
        return _default_persons()
    return sorted([
        s["attributes"].get("friendly_name", s["entity_id"].split(".")[1])
        for s in data
        if s["entity_id"].startswith("person.")
    ])


def _default_rooms() -> list[str]:
    return ["Küche", "Wohnzimmer", "Schlafzimmer", "Bad", "Flur", "Keller", "Garten", "Garage"]


def _default_persons() -> list[str]:
    return ["Danny", "Marina"]
