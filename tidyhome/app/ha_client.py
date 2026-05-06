import os
import json
import aiohttp
import logging

logger = logging.getLogger("tidyhome.ha")

SUPERVISOR_TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")
HA_BASE = "http://supervisor/core/api"


async def _render_template(template: str) -> str | None:
    if not SUPERVISOR_TOKEN:
        return None
    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{HA_BASE}/template",
                headers=headers,
                json={"template": template},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as r:
                if r.status == 200:
                    return await r.text()
                logger.warning("Template API returned %s: %s", r.status, await r.text())
    except Exception as e:
        logger.warning("HA template error: %s", e)
    return None


async def _get(path: str) -> dict | list | None:
    if not SUPERVISOR_TOKEN:
        return None
    headers = {"Authorization": f"Bearer {SUPERVISOR_TOKEN}"}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{HA_BASE}{path}",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as r:
                if r.status == 200:
                    return await r.json()
                logger.warning("HA API %s returned %s", path, r.status)
    except Exception as e:
        logger.warning("HA API error %s: %s", path, e)
    return None


async def get_areas() -> list[str]:
    raw = await _render_template(
        "{{ areas() | map('area_name') | list | tojson }}"
    )
    if not raw:
        return _default_rooms()
    try:
        names = json.loads(raw)
        if names:
            return sorted([n for n in names if n])
    except Exception as e:
        logger.warning("Areas parse error: %s (raw=%r)", e, raw)
    return _default_rooms()


async def get_persons() -> list[str]:
    data = await _get("/states")
    if not data:
        return _default_persons()
    persons = sorted([
        s["attributes"].get("friendly_name", s["entity_id"].split(".", 1)[1])
        for s in data
        if s["entity_id"].startswith("person.")
    ])
    return persons or _default_persons()


def _default_rooms() -> list[str]:
    return ["Küche", "Wohnzimmer", "Schlafzimmer", "Bad", "Flur", "Keller", "Garten", "Garage"]


def _default_persons() -> list[str]:
    return ["Danny", "Marina"]
