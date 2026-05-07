from fastapi import Request
from fastapi.responses import HTMLResponse
from storage import get_admins

INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}

ROOM_ICONS = {
    "Küche": "KI", "Wohnzimmer": "WO", "Schlafzimmer": "SZ", "Bad": "BD",
    "Badezimmer": "BD", "Flur": "FL", "Keller": "KE", "Garten": "GA",
    "Garage": "GR", "Büro": "BU", "Arbeitszimmer": "AR", "Esszimmer": "EZ",
    "Kinderzimmer": "KZ", "Balkon": "BA", "Terrasse": "TE",
}

# ── SVG icon paths (Feather-style 24×24) ─────────────────────────────────────
_ICON_PATHS: dict[str, str] = {
    "home":      '<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "tasks":     '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>',
    "projects":  '<path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>',
    "scores":    '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "person":    '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "check":     '<polyline points="20 6 9 17 4 12"/>',
    "edit":      '<path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>',
    "trash":     '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6m3 0V4h8v2"/>',
    "bell":      '<path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/>',
    "more":      '<circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>',
    "search":    '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "plus":      '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "chevron_r": '<polyline points="9 18 15 12 9 6"/>',
    "chevron_l": '<polyline points="15 18 9 12 15 6"/>',
    "calendar":  '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "vacuum":    '<circle cx="9" cy="13" r="5"/><path d="M14 13h4l2-4V7h-6"/><line x1="9" y1="18" x2="9" y2="21"/>',
    "trash_bin": '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6m5 0V4h4v2m-3 4v6m4-6v6"/>',
    "plant":     '<path d="M12 22V12"/><path d="M12 12C12 7 7 5 7 5s1 5 5 7"/><path d="M12 12c0-5 5-7 5-7s-1 5-5 7"/>',
    "box":       '<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "hanger":    '<path d="M20.38 18.57L12 13 3.62 18.57A2 2 0 005 22h14a2 2 0 001.38-3.43z"/><path d="M12 13V7"/><circle cx="12" cy="5" r="2"/>',
    "broom":     '<path d="M8 19l-5 2 2-5L16 5l3 3L8 19z"/><path d="M16 5l3 3"/>',
    "drop":      '<path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/>',
    "star":      '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "archive":   '<polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/>',
    "settings":  '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>',
}

# Navigation items: (icon_key, label, page_key, href)
_NAV_ITEMS = [
    ("home",     "Zuhause",    "home",     "./"),
    ("tasks",    "Aufgaben",   "tasks",    "tasks"),
    ("projects", "Projekte",   "projects", "projects"),
    ("scores",   "Punkte",     "scores",   "scores"),
    ("person",   "Ich",        "settings", "settings"),
]


def _icon(name: str, size: int = 20, color: str = "currentColor", sw: float = 2.0) -> str:
    """Inline SVG icon (Feather-style)."""
    path = _ICON_PATHS.get(name, _ICON_PATHS["tasks"])
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
        f'stroke="{color}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" style="display:block;flex-shrink:0">'
        f'{path}</svg>'
    )


# OpenMoji icon filename + bubble background per task category
# filename = Unicode hex codepoint as used by openmoji (assets/icons/<filename>.svg)
_TASK_ICONS: dict[str, tuple[str, str]] = {
    # key: (openmoji_filename, bubble_bg)
    "besen":      ("1F9F9",      "var(--primary-soft)"),    # 🧹 Fegen/Staubsaugen
    "schwamm":    ("1F9FD",      "var(--primary-soft)"),    # 🧽 Schrubben
    "putzen":     ("1FAE7",      "var(--primary-soft)"),    # 🫧 Putzen allgemein
    "eimer":      ("1FAA3",      "rgba(59,130,246,0.12)"),  # 🪣 Wischen/Eimer
    "dusche":     ("1F6BF",      "rgba(59,130,246,0.12)"),  # 🚿 Dusche
    "bad":        ("1F6C1",      "rgba(59,130,246,0.12)"),  # 🛁 Badewanne
    "toilette":   ("1F6BD",      "var(--surface-2)"),       # 🚽 Toilette
    "papier":     ("1F9FB",      "var(--surface-2)"),       # 🧻 Toilettenpapier
    "kochen":     ("1F373",      "var(--warning-bg)"),      # 🍳 Kochen
    "abwasch":    ("1F37D-FE0F", "var(--surface-2)"),       # 🍽️ Spülen/Abwasch
    "kuehlschrank":("1F9CA",     "rgba(59,130,246,0.12)"),  # 🧊 Kühlschrank
    "lunchbox":   ("1F371",      "var(--warning-bg)"),      # 🍱 Lunchbox/Brotdose
    "waesche":    ("1F9FA",      "var(--primary-soft)"),    # 🧺 Wäsche waschen
    "buegeln":    ("1F455",      "var(--primary-soft)"),    # 👕 Bügeln/Kleidung
    "pflanze":    ("1FAB4",      "var(--success-bg)"),      # 🪴 Zimmerpflanze
    "garten":     ("1F33F",      "var(--success-bg)"),      # 🌿 Garten
    "laub":       ("1F342",      "var(--warning-bg)"),      # 🍂 Laub harken
    "saen":       ("1F331",      "var(--success-bg)"),      # 🌱 Säen/Balkon
    "schnee":     ("2744-FE0F",  "rgba(59,130,246,0.12)"),  # ❄️ Schnee schippen
    "blumen":     ("1F490",      "var(--success-bg)"),      # 💐 Blumen
    "muell":      ("1F5D1-FE0F", "var(--surface-2)"),       # 🗑️ Müll rausbringen
    "recycling":  ("267B-FE0F",  "var(--success-bg)"),      # ♻️ Recycling/Trennen
    "einkaufen":  ("1F6D2",      "var(--warning-bg)"),      # 🛒 Einkaufen
    "post":       ("1F4EC",      "var(--primary-soft)"),    # 📬 Post holen
    "tier":       ("1F43E",      "var(--warning-bg)"),      # 🐾 Haustier allgemein
    "hund":       ("1F415",      "var(--warning-bg)"),      # 🐕 Hund
    "katze":      ("1F408",      "var(--surface-2)"),       # 🐈 Katze
    "werkzeug":   ("1F9F0",      "var(--warning-bg)"),      # 🧰 Reparatur
    "schraube":   ("1F527",      "var(--warning-bg)"),      # 🔧 Schraubenschlüssel
    "gluehbirne": ("1F4A1",      "var(--warning-bg)"),      # 💡 Glühbirne
    "batterie":   ("1F50B",      "var(--surface-2)"),       # 🔋 Batterie/Filter
    "schluessel": ("1F511",      "var(--warning-bg)"),      # 🔑 Sicherheit/Schloss
    "buecher":    ("1F4DA",      "var(--primary-soft)"),    # 📚 Hausaufgaben
    "rucksack":   ("1F392",      "var(--primary-soft)"),    # 🎒 Schule
    "medizin":    ("1F48A",      "var(--danger-bg)"),       # 💊 Apotheke/Medizin
    "bett":       ("1F6CF-FE0F", "var(--primary-soft)"),    # 🛏️ Bett machen
    "fenster":    ("1FA9F",      "rgba(59,130,246,0.12)"),  # 🪟 Fenster/Lüften
    "bad_auffuel":("1F9F4",      "var(--primary-soft)"),    # 🧴 Bad auffüllen
    "lager":      ("1F4E6",      "var(--warning-bg)"),      # 📦 Keller/Lager
    "auto":       ("1F697",      "var(--surface-2)"),       # 🚗 Auto
    "tanken":     ("26FD",       "var(--surface-2)"),       # ⛽ Tanken
    "heizung":    ("1F321-FE0F", "var(--warning-bg)"),      # 🌡️ Heizung/Thermostat
    "default":    ("1F3E0",      "var(--primary-soft)"),    # 🏠 Allgemein
}


def _task_icon_key(name: str, room: str = "") -> str:
    n = (name + " " + room).lower()
    if any(w in n for w in ["staub", "saug", "feg", "besen"]):         return "besen"
    if any(w in n for w in ["schrub", "schwamm"]):                      return "schwamm"
    if any(w in n for w in ["putz", "wisch", "reinig", "scheuer"]):     return "putzen"
    if any(w in n for w in ["eimer", "mopp"]):                          return "eimer"
    if any(w in n for w in ["dusch"]):                                   return "dusche"
    if any(w in n for w in ["wanne", "badewanne"]):                     return "bad"
    if any(w in n for w in ["toilett", "klo", "wc"]):                   return "toilette"
    if any(w in n for w in ["klopapier", "papierhandtuch", "toilettenpapier"]): return "papier"
    if any(w in n for w in ["koch", "backen", "herd", "ofen"]):         return "kochen"
    if any(w in n for w in ["abwasch", "spül", "geschirr", "spülmaschine"]): return "abwasch"
    if any(w in n for w in ["kühlschrank", "kühlung", "gefrier"]):      return "kuehlschrank"
    if any(w in n for w in ["lunchbox", "brotdose", "vesper"]):         return "lunchbox"
    if any(w in n for w in ["wäsch", "waschen", "waschmaschine"]):      return "waesche"
    if any(w in n for w in ["bügel", "kleid", "garderob", "hänger"]):   return "buegeln"
    if any(w in n for w in ["pflanz", "blum", "gieß"]) and \
       any(w in n for w in ["zimmer", "topf", "innen"]):                return "pflanze"
    if any(w in n for w in ["gieß", "pflanz"]):                         return "pflanze"
    if any(w in n for w in ["garten", "rasen", "mäh", "unkraut", "hecke"]): return "garten"
    if any(w in n for w in ["laub", "herbst", "harken"]):               return "laub"
    if any(w in n for w in ["säen", "aussät", "pflanzen"]):             return "saen"
    if any(w in n for w in ["schnee", "schaufeln"]):                    return "schnee"
    if any(w in n for w in ["blumen", "bouquet", "blumenstrauß"]):      return "blumen"
    if any(w in n for w in ["müll", "abfall", "entsorg", "tonne"]):     return "muell"
    if any(w in n for w in ["recycling", "recycle", "trennen", "papier", "glas", "kompost"]): return "recycling"
    if any(w in n for w in ["einkauf", "supermarkt", "shop", "besorg"]): return "einkaufen"
    if any(w in n for w in ["post", "brief", "paket", "briefkasten"]): return "post"
    if any(w in n for w in ["hund", "gassi"]):                          return "hund"
    if any(w in n for w in ["katze", "kater"]):                         return "katze"
    if any(w in n for w in ["tier", "haustier", "futter", "tierarzt", "pfoten"]): return "tier"
    if any(w in n for w in ["reparier", "werkzeug", "heimwerk"]):       return "werkzeug"
    if any(w in n for w in ["schrauben", "montier", "aufbau"]):         return "schraube"
    if any(w in n for w in ["lampe", "glühbirne", "leuchtmittel"]):     return "gluehbirne"
    if any(w in n for w in ["batterie", "akku", "filter wechsel"]):     return "batterie"
    if any(w in n for w in ["schloss", "schlüssel", "abschließ", "sicherheit"]): return "schluessel"
    if any(w in n for w in ["hausaufgaben", "lernen", "nachhilfe"]):    return "buecher"
    if any(w in n for w in ["schule", "rucksack", "ranzen"]):           return "rucksack"
    if any(w in n for w in ["apotheke", "arzt", "medizin", "tabletten"]): return "medizin"
    if any(w in n for w in ["bett", "bettwäsche", "laken", "kissen"]):  return "bett"
    if any(w in n for w in ["fenster", "lüften"]):                      return "fenster"
    if any(w in n for w in ["seife", "duschgel", "shampoo", "creme", "lotion"]): return "bad_auffuel"
    if any(w in n for w in ["keller", "lager", "box", "karton", "stauraum"]): return "lager"
    if any(w in n for w in ["auto", "wagen", "kfz", "waschen"]) and \
       any(w in n for w in ["auto", "wagen", "kfz"]):                   return "auto"
    if any(w in n for w in ["tanken", "tankstelle", "kraftstoff"]):     return "tanken"
    if any(w in n for w in ["heizung", "thermostat", "heizkörper", "temperatur"]): return "heizung"
    return "default"


def _task_icon(name: str, room: str = "", size: int = 44) -> str:
    """Round icon bubble using OpenMoji SVG for a task."""
    key = _task_icon_key(name, room)
    filename, bg = _TASK_ICONS.get(key, _TASK_ICONS["default"])
    img_size = int(size * 0.62)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:{bg};display:flex;align-items:center;'
        f'justify-content:center;flex-shrink:0;overflow:hidden">'
        f'<img src="assets/icons/{filename}.svg" width="{img_size}" height="{img_size}"'
        f' style="display:block" loading="lazy">'
        f'</div>'
    )


def _proj_icon(room: str = "", size: int = 46) -> str:
    """Round icon bubble for a project, based on room."""
    r = room.lower()
    if any(w in r for w in ["keller", "lager"]): key = "box"
    elif any(w in r for w in ["bad", "küche"]): key = "drop"
    elif any(w in r for w in ["garten", "balkon"]): key = "plant"
    elif any(w in r for w in ["schlaf", "kinder"]): key = "hanger"
    else: key = "archive"
    inner = int(size * 0.46)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:var(--icon-bg);display:flex;align-items:center;'
        f'justify-content:center;flex-shrink:0">'
        f'{_icon(key, inner, "var(--icon-color)")}'
        f'</div>'
    )


def _ring_chart(value_str: str, pct: int, color: str, label: str, size: int = 70) -> str:
    """SVG donut ring chart with center text label."""
    safe_pct = max(0, min(pct, 100))
    return (
        f'<div style="text-align:center">'
        f'<div style="position:relative;width:{size}px;height:{size}px;margin:0 auto 0.4rem">'
        f'<svg viewBox="0 0 36 36" width="{size}" height="{size}" style="transform:rotate(-90deg)">'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="var(--ring-bg)" stroke-width="3"/>'
        f'<circle cx="18" cy="18" r="15.9" fill="none" stroke="{color}" stroke-width="3"'
        f' stroke-dasharray="{safe_pct} 100" stroke-linecap="round"/>'
        f'</svg>'
        f'<div style="position:absolute;inset:0;display:flex;align-items:center;'
        f'justify-content:center;font-size:0.82rem;font-weight:800;color:var(--text)">'
        f'{value_str}</div>'
        f'</div>'
        f'<div style="font-size:0.65rem;color:var(--muted);font-weight:600;'
        f'text-transform:uppercase;letter-spacing:0.05em">{label}</div>'
        f'</div>'
    )


def interval_label(days: int) -> str:
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:  return "overdue"
    if days == 0: return "today"
    if days <= 3: return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def resolve_person(request: Request, p_param: str = "") -> str:
    ha_user = (
        request.headers.get("X-Remote-User-Display-Name") or
        request.headers.get("X-Remote-User-Name", "")
    ).strip()
    if p_param and ha_user in get_admins():
        return p_param
    return ha_user or p_param


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


_CSS = """
  :root {
    --primary: #b5738a;
    --primary-dark: #8f4f65;
    --primary-light: #f9f0f4;
    --primary-border: #e8c8d4;
    --bg: #f4eff2;
    --card: #ffffff;
    --text: #2d1f26;
    --muted: #9b8890;
    --border: #ede8eb;
    --success: #4a9e6b;
    --success-bg: #e8f5ee;
    --warning: #c47c1a;
    --warning-bg: #fef3e2;
    --danger: #c53030;
    --danger-bg: #fee2e2;
    --ring-bg: #e8e0e4;
    --icon-bg: #f0e8ed;
    --icon-color: #8f4f65;
    --nav-h: 4.25rem;
    --radius: 1.1rem;
    --shadow: 0 2px 8px rgba(45,31,38,0.07);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #181316;
      --card: #231a20;
      --text: #ede5e9;
      --muted: #8a7a82;
      --border: #362630;
      --primary-light: #2e1e28;
      --primary-border: #5a3347;
      --success-bg: #0f2a1c;
      --warning-bg: #2a1e08;
      --danger-bg: #2a0f0f;
      --ring-bg: #362630;
      --icon-bg: #2e1e28;
      --icon-color: #c98aa0;
      --shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    header, .bottom-nav { background: var(--card); border-color: var(--border); }
    input, select { background: #2a1e24; color: var(--text); border-color: var(--border); }
    .filter-btn { background: var(--card); color: var(--text); border-color: var(--border); }
    .filter-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg); color: var(--text);
    padding-bottom: calc(var(--nav-h) + 0.5rem);
  }
  header {
    background: var(--card); border-bottom: 1px solid var(--border);
    padding: 0.75rem 1.25rem;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 10;
    box-shadow: var(--shadow);
  }
  .h-left { display: flex; align-items: center; gap: 0.5rem; }
  .h-logo { font-size: 1.35rem; }
  .h-title { font-size: 1.05rem; font-weight: 700; color: var(--primary-dark); }
  .h-pill {
    font-size: 0.78rem; background: var(--primary-light);
    color: var(--primary-dark); padding: 0.22rem 0.75rem;
    border-radius: 999px; border: 1px solid var(--primary-border);
    text-decoration: none; font-weight: 600;
  }
  .bottom-nav {
    position: fixed; bottom: 0; left: 0; right: 0; height: var(--nav-h);
    background: var(--card); border-top: 1px solid var(--border);
    display: flex; z-index: 10;
    box-shadow: 0 -2px 12px rgba(0,0,0,0.07);
  }
  .nav-item {
    flex: 1; display: flex; flex-direction: column; align-items: center;
    justify-content: center; gap: 0.2rem;
    text-decoration: none; color: var(--muted); font-size: 0.62rem;
    font-weight: 600; transition: color 0.15s; padding: 0.4rem 0;
    letter-spacing: 0.01em;
  }
  .nav-item.active { color: var(--primary); }
  main { padding: 1.25rem; max-width: 640px; margin: 0 auto; }
  .card {
    background: var(--card); border-radius: var(--radius); padding: 1.25rem;
    box-shadow: var(--shadow); margin-bottom: 1rem;
  }
  .card-flush { padding: 0; overflow: hidden; }
  h2 { font-size: 1rem; font-weight: 700; margin-bottom: 0.875rem; }
  h3 { font-size: 0.9rem; font-weight: 600; }
  .muted { color: var(--muted); font-size: 0.8rem; }
  /* Task rows */
  .task-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.875rem 1.25rem; border-bottom: 1px solid var(--border);
  }
  .task-row:last-child { border-bottom: none; }
  .task-name { font-weight: 600; font-size: 0.9rem; }
  .task-meta { font-size: 0.74rem; color: var(--muted); }
  .task-date {
    display: flex; align-items: center; gap: 0.3rem;
    font-size: 0.74rem; color: var(--muted); margin-top: 0.2rem;
  }
  .task-actions { display: flex; align-items: center; gap: 0.2rem; flex-shrink: 0; }
  /* Icon buttons */
  .icon-btn {
    width: 34px; height: 34px; border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    border: none; cursor: pointer; background: transparent;
    color: var(--muted); transition: all 0.15s; text-decoration: none;
    flex-shrink: 0;
  }
  .icon-btn:hover { background: var(--border); color: var(--text); }
  .icon-btn.success { color: var(--success); }
  .icon-btn.success:hover { background: var(--success-bg); }
  .icon-btn.danger { color: var(--danger); }
  .icon-btn.danger:hover { background: var(--danger-bg); }
  form.inline { display: inline; }
  /* Badges */
  .badge {
    display: inline-flex; align-items: center;
    padding: 0.15rem 0.55rem; border-radius: 999px;
    font-size: 0.69rem; font-weight: 700; white-space: nowrap;
  }
  .overdue { background: var(--danger-bg);  color: var(--danger); }
  .today   { background: var(--warning-bg); color: var(--warning); }
  .soon    { background: #fef9e7;           color: #92610a; }
  .ok      { background: var(--success-bg); color: var(--success); }
  /* Old-style buttons (still used in forms) */
  .btn {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 0.45rem 1rem; border-radius: 0.55rem; border: none;
    cursor: pointer; font-size: 0.84rem; font-weight: 600;
    text-decoration: none; transition: opacity 0.15s; gap: 0.3rem;
  }
  .btn:hover { opacity: 0.82; }
  .btn-primary { background: var(--primary); color: white; }
  .btn-success { background: var(--success); color: white; }
  .btn-danger  { background: var(--danger);  color: white; }
  .btn-ghost {
    background: var(--primary-light); color: var(--primary-dark);
    border: 1px solid var(--primary-border);
  }
  .btn-sm { padding: 0.22rem 0.55rem; font-size: 0.76rem; border-radius: 0.4rem; }
  .btn-full { width: 100%; padding: 0.8rem; font-size: 0.95rem; border-radius: 0.75rem; }
  /* Forms */
  .form-group { margin-bottom: 1rem; }
  label {
    display: block; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.04em;
    text-transform: uppercase; margin-bottom: 0.3rem; color: var(--muted);
  }
  input, select {
    width: 100%; padding: 0.6rem 0.875rem;
    border: 1.5px solid var(--border); border-radius: 0.6rem;
    font-size: 0.9rem; color: var(--text); background: var(--card);
    transition: border-color 0.15s;
  }
  input:focus, select:focus { outline: none; border-color: var(--primary); }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  /* Filters */
  .filters {
    display: flex; gap: 0.4rem; margin-bottom: 1rem;
    flex-wrap: wrap; overflow-x: auto; padding-bottom: 0.1rem;
  }
  .filter-btn {
    padding: 0.3rem 0.9rem; border-radius: 999px;
    border: 1.5px solid var(--border); background: var(--card);
    cursor: pointer; font-size: 0.76rem; white-space: nowrap;
    text-decoration: none; color: var(--muted); transition: all 0.15s;
    font-weight: 600;
  }
  .filter-btn.active {
    background: var(--primary); color: white; border-color: var(--primary);
  }
  /* Scores */
  .score-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.75rem 0; border-bottom: 1px solid var(--border);
  }
  .score-row:last-child { border-bottom: none; }
  .score-name { flex: 1; font-weight: 600; }
  .score-pts { font-size: 1.1rem; font-weight: 700; color: var(--primary); }
  /* Progress */
  .progress-track { background: var(--ring-bg); border-radius: 999px; height: 5px; }
  .progress-fill  { background: var(--primary); height: 5px; border-radius: 999px; transition: width 0.3s; }
  .progress-fill.green { background: var(--success); }
  /* Stat cards */
  .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; margin-bottom: 1rem; }
  .stat-card {
    background: var(--card); border-radius: var(--radius); padding: 1rem 0.75rem;
    box-shadow: var(--shadow); text-align: center;
  }
  .stat-value { font-size: 2rem; font-weight: 800; color: var(--primary); line-height: 1; }
  .stat-value.green { color: var(--success); }
  .stat-label { font-size: 0.72rem; color: var(--muted); margin-top: 0.3rem; font-weight: 500; }
  /* Room grid/list */
  .room-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
  .room-card {
    background: var(--card); border-radius: var(--radius); padding: 1rem;
    box-shadow: var(--shadow); text-decoration: none; color: var(--text); display: block;
    transition: box-shadow 0.15s;
  }
  .room-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
  .room-icon { font-size: 1.6rem; margin-bottom: 0.35rem; }
  .room-name { font-weight: 700; font-size: 0.88rem; margin-bottom: 0.15rem; }
  .room-count { font-size: 0.72rem; color: var(--muted); margin-bottom: 0.4rem; }
  /* Project cards */
  .proj-row {
    display: flex; align-items: center; gap: 0.875rem;
    padding: 1rem 1.25rem; border-bottom: 1px solid var(--border);
  }
  .proj-row:last-child { border-bottom: none; }
  /* Empty + info */
  .empty {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 3rem 1.5rem; color: var(--muted); font-size: 0.88rem; gap: 0.5rem;
    text-align: center;
  }
  .empty-icon { font-size: 2.5rem; opacity: 0.4; margin-bottom: 0.25rem; }
  .info-box {
    background: var(--primary-light); border: 1px solid var(--primary-border);
    border-radius: 0.75rem; padding: 0.875rem; margin-bottom: 1rem;
    font-size: 0.82rem; color: var(--primary-dark);
  }
  .admin-badge {
    font-size: 0.7rem; background: var(--primary-light); color: var(--primary-dark);
    padding: 0.1rem 0.5rem; border-radius: 999px; border: 1px solid var(--primary-border);
  }
  .page-header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 1rem;
  }
"""


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    psuffix = f"?p={person}" if person else ""
    admins = get_admins()

    # Person nav pill
    if not person:
        person_nav = '<a href="settings" class="h-pill">Wer bin ich?</a>'
    elif person in admins:
        person_nav = f'<a href="settings{psuffix}" class="h-pill">{person} ▾</a>'
    else:
        person_nav = f'<span class="h-pill">{person}</span>'

    # Header icons
    bell_icon = _icon("bell", 20, "var(--muted)")
    more_icon = _icon("more", 20, "var(--muted)")

    # Bottom navigation with SVG icons
    nav_items = ""
    for icon_key, label, page_key, href in _NAV_ITEMS:
        active = "active" if page == page_key else ""
        nav_items += (
            f'<a href="{href}{psuffix}" class="nav-item {active}">'
            f'{_icon(icon_key, 22)}'
            f'<span>{label}</span>'
            f'</a>'
        )

    html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<base href="{base}">
<title>TidyHome</title>
<link rel="icon" type="image/svg+xml" href="assets/logo.svg">
<style>
  html,body{{background:#f6f7f9;color:#20242a}}
  header{{background:rgba(255,255,255,0.88);border-bottom:1px solid #dde2e8}}
  .bottom-nav{{background:rgba(255,255,255,0.94);border-top:1px solid #dde2e8}}
  @media(prefers-color-scheme:dark){{
    html,body{{background:#101114;color:#f4f1f2}}
    header,.bottom-nav{{background:rgba(24,26,31,0.92);border-color:#30333b}}
  }}
</style>
<link rel="stylesheet" href="assets/app.css">
</head>
<body>
<header>
  <div class="h-left">
    <img src="assets/logo.svg" style="width:28px;height:28px;border-radius:7px">
    <span class="h-title">TidyHome</span>
  </div>
  <div style="display:flex;gap:0.5rem;align-items:center">
    {person_nav}
    <button style="background:none;border:none;cursor:pointer;color:var(--muted);
                   display:flex;align-items:center;padding:0.3rem">{bell_icon}</button>
    <button style="background:none;border:none;cursor:pointer;color:var(--muted);
                   display:flex;align-items:center;padding:0.3rem">{more_icon}</button>
  </div>
</header>
<main>
{content}
</main>
<nav class="bottom-nav">{nav_items}</nav>
</body>
</html>"""

    return HTMLResponse(html)
