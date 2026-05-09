from urllib.parse import quote
from datetime import date, datetime
from html import escape

from fastapi import Request
from fastapi.responses import HTMLResponse
from storage import (get_admins, get_vacation_mode, is_vacation_mode_active,
                     count_photos, list_comments, list_photos)

INTERVALS = {
    1: "Täglich", 2: "Alle 2 Tage", 7: "Wöchentlich", 14: "Alle 2 Wochen",
    30: "Monatlich", 90: "Vierteljährlich", 180: "Halbjährlich", 365: "Jährlich",
}

# Room name -> (openmoji_filename, bubble_bg)
ROOM_ICONS: dict[str, tuple[str, str]] = {
    "Küche":        ("1F373",      "var(--warning-bg)"),
    "Wohnzimmer":   ("1F6CB",      "var(--primary-soft)"),
    "Schlafzimmer": ("1F6CF-FE0F", "rgba(59,130,246,0.12)"),
    "Bad":          ("1F6C0",      "rgba(59,130,246,0.12)"),
    "Badezimmer":   ("1F6C0",      "rgba(59,130,246,0.12)"),
    "Flur":         ("1F6AA",      "var(--surface-2)"),
    "Keller":       ("1F4E6",      "var(--surface-2)"),
    "Garten":       ("1F333",      "var(--success-bg)"),
    "Garage":       ("1F697",      "var(--surface-2)"),
    "Büro":         ("1F4BB",      "var(--primary-soft)"),
    "Arbeitszimmer":("1F4BB",      "var(--primary-soft)"),
    "Esszimmer":    ("1F37D-FE0F", "var(--warning-bg)"),
    "Kinderzimmer": ("1F392",      "var(--primary-soft)"),
    "Balkon":       ("1FAB4",      "var(--success-bg)"),
    "Terrasse":     ("2600",       "var(--warning-bg)"),
}

ROOM_ICON_CHOICES: dict[str, tuple[str, str]] = {
    "kitchen":             ("1F373",      "var(--warning-bg)"),
    "dining_room":         ("1F37D-FE0F", "var(--warning-bg)"),
    "living_room":         ("1F6CB",      "var(--primary-soft)"),
    "living_room_tv":      ("1F4FA",      "var(--primary-soft)"),
    "bedroom":             ("1F6CF-FE0F", "rgba(59,130,246,0.12)"),
    "bathroom":            ("1F6C0",      "rgba(59,130,246,0.12)"),
    "shower":              ("1F6BF",      "rgba(59,130,246,0.12)"),
    "toilet":              ("1F6BD",      "rgba(59,130,246,0.12)"),
    "sink":                ("1F6C1",      "rgba(59,130,246,0.12)"),
    "bubbles":             ("1FAE7",      "rgba(59,130,246,0.12)"),
    "hallway":             ("1F6AA",      "var(--surface-2)"),
    "office":              ("1F4BB",      "var(--primary-soft)"),
    "library":             ("1F4DA",      "var(--primary-soft)"),
    "kids_room":           ("1F392",      "var(--primary-soft)"),
    "wardrobe":            ("1F455",      "var(--primary-soft)"),
    "laundry":             ("1F9FA",      "var(--primary-soft)"),
    "cleaning_room":       ("1F9F9",      "var(--success-bg)"),
    "cleaning_sponge":     ("1F9FD",      "var(--success-bg)"),
    "basement":            ("1F4E6",      "var(--surface-2)"),
    "storage":             ("1F4E6",      "var(--warning-bg)"),
    "home":                ("1F3E0",      "var(--primary-soft)"),
    "garden":              ("1F333",      "var(--success-bg)"),
    "garden_bed":          ("1F33F",      "var(--success-bg)"),
    "seedling":            ("1F331",      "var(--success-bg)"),
    "sunflower":           ("1F33B",      "var(--warning-bg)"),
    "flowers":             ("1F490",      "var(--success-bg)"),
    "balcony":             ("1FAB4",      "var(--success-bg)"),
    "terrace":             ("2600",       "var(--warning-bg)"),
    "terrace_umbrella":    ("26F1-FE0F",  "var(--warning-bg)"),
    "property":            ("1F3E1",      "var(--success-bg)"),
    "car":                 ("1F697",      "var(--surface-2)"),
    "suv":                 ("1F698",      "var(--surface-2)"),
    "gas_station":         ("26FD",       "var(--warning-bg)"),
    "bike":                ("1F6B2",      "var(--success-bg)"),
    "scooter":             ("1F6F5",      "var(--surface-2)"),
    "motorcycle":          ("1F3CD-FE0F", "var(--surface-2)"),
    "work":                ("1F3E2",      "var(--primary-soft)"),
    "briefcase":           ("1F4BC",      "var(--primary-soft)"),
    "school":              ("1F3EB",      "var(--warning-bg)"),
    "doctor":              ("1F3E5",      "rgba(59,130,246,0.12)"),
    "shop":                ("1F3EA",      "var(--warning-bg)"),
    "shopping":            ("1F6D2",      "var(--warning-bg)"),
    "authority":           ("1F3DB-FE0F", "var(--surface-2)"),
    "bank":                ("1F3E6",      "var(--primary-soft)"),
    "post_office":         ("1F3E3",      "var(--warning-bg)"),
    "beach":               ("1F3D6-FE0F", "var(--warning-bg)"),
    "island":              ("1F3DD-FE0F", "var(--success-bg)"),
    "ski_mountain":        ("1F3D4-FE0F", "rgba(59,130,246,0.12)"),
    "hiking_mountain":     ("26F0-FE0F",  "var(--surface-2)"),
    "camping":             ("1F3D5-FE0F", "var(--success-bg)"),
    "tent":                ("26FA",       "var(--warning-bg)"),
    "hotel":               ("1F3E8",      "var(--primary-soft)"),
    "travel_plane":        ("2708-FE0F",  "rgba(59,130,246,0.12)"),
    "travel_world":        ("1F30D",      "var(--success-bg)"),
    "luggage":             ("1F9F3",      "var(--warning-bg)"),
    "dog":                 ("1F415",      "var(--warning-bg)"),
    "cat":                 ("1F408",      "var(--warning-bg)"),
    "pets":                ("1F43E",      "var(--warning-bg)"),
    "aquarium":            ("1F41F",      "rgba(59,130,246,0.12)"),
    "chicken_coop":        ("1F414",      "var(--warning-bg)"),
    "stable":              ("1F40E",      "var(--warning-bg)"),
    "gym":                 ("1F3CB-FE0F", "var(--primary-soft)"),
    "atelier":             ("1F3A8",      "var(--primary-soft)"),
    "workshop":            ("1F527",      "var(--surface-2)"),
    "toolbox":             ("1F9F0",      "var(--surface-2)"),
    "music_guitar":        ("1F3B8",      "var(--primary-soft)"),
    "music_piano":         ("1F3B9",      "var(--primary-soft)"),
    "gaming":              ("1F3AE",      "var(--primary-soft)"),
    "wine_cellar":         ("1F377",      "var(--warning-bg)"),
    "home_bar":            ("1F37A",      "var(--warning-bg)"),
    "seasonal_christmas":  ("1F384",      "var(--success-bg)"),
    "sewing":              ("1FAA1",      "var(--primary-soft)"),
    "thread":              ("1F9F5",      "var(--primary-soft)"),
}

ROOM_ICON_LABELS: dict[str, str] = {
    "kitchen": "Küche",
    "dining_room": "Esszimmer",
    "living_room": "Wohnzimmer",
    "living_room_tv": "Fernseher",
    "bedroom": "Schlafzimmer",
    "bathroom": "Bad",
    "shower": "Dusche",
    "toilet": "Toilette",
    "sink": "Waschbecken",
    "bubbles": "Seifenblasen",
    "hallway": "Flur",
    "office": "Büro",
    "library": "Bibliothek",
    "kids_room": "Kinderzimmer",
    "wardrobe": "Ankleide",
    "laundry": "Wäsche",
    "cleaning_room": "Putzraum",
    "cleaning_sponge": "Schwamm",
    "basement": "Keller",
    "storage": "Lager",
    "home": "Allgemein",
    "garden": "Garten",
    "garden_bed": "Beet",
    "seedling": "Aussaat",
    "sunflower": "Sonnenblume",
    "flowers": "Blumen",
    "balcony": "Balkon",
    "terrace": "Terrasse",
    "terrace_umbrella": "Sonnenschirm",
    "property": "Grundstück",
    "car": "Auto",
    "suv": "Zweitwagen",
    "gas_station": "Tanken",
    "bike": "Fahrrad",
    "scooter": "Roller",
    "motorcycle": "Motorrad",
    "work": "Arbeit",
    "briefcase": "Aktentasche",
    "school": "Schule",
    "doctor": "Arzt",
    "shop": "Geschäft",
    "shopping": "Einkaufen",
    "authority": "Behörde",
    "bank": "Bank",
    "post_office": "Post",
    "beach": "Strand",
    "island": "Insel",
    "ski_mountain": "Skiurlaub",
    "hiking_mountain": "Wandern",
    "camping": "Camping",
    "tent": "Zelt",
    "hotel": "Hotel",
    "travel_plane": "Reise",
    "travel_world": "Welt",
    "luggage": "Koffer",
    "dog": "Hund",
    "cat": "Katze",
    "pets": "Haustiere",
    "aquarium": "Aquarium",
    "chicken_coop": "Hühnerstall",
    "stable": "Stall",
    "gym": "Fitnessraum",
    "atelier": "Atelier",
    "workshop": "Werkstatt",
    "toolbox": "Werkzeugkasten",
    "music_guitar": "Musikzimmer",
    "music_piano": "Klavier",
    "gaming": "Gaming",
    "wine_cellar": "Weinkeller",
    "home_bar": "Hausbar",
    "seasonal_christmas": "Saison",
    "sewing": "Nähzimmer",
    "thread": "Garn",
}

ROOM_ICON_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("toilet", ("toilette", "wc", "gäste-wc", "gaeste-wc", "klo")),
    ("shower", ("dusche", "duschbad")),
    ("sink", ("waschbecken", "spüle", "spuele")),
    ("laundry", ("wäsche", "waesche", "waschküche", "waschkueche", "hauswirtschaft")),
    ("cleaning_room", ("putzraum", "besenkammer", "reinigung")),
    ("workshop", ("werkstatt",)),
    ("bike", ("fahrrad", "rad", "bike")),
    ("scooter", ("roller",)),
    ("motorcycle", ("motorrad",)),
    ("car", ("garage", "auto", "carport", "stellplatz")),
    ("bathroom", ("badezimmer", "bad")),
    ("kitchen", ("küche", "kueche", "kochküche", "koch", "pantry")),
    ("dining_room", ("esszimmer", "speisezimmer", "essen")),
    ("living_room", ("wohnzimmer", "wohnraum", "stube", "lounge")),
    ("bedroom", ("schlafzimmer", "schlafraum", "gästezimmer", "gaestezimmer")),
    ("kids_room", ("kinderzimmer", "spielzimmer", "babyzimmer")),
    ("office", ("büro", "buero", "arbeitszimmer", "homeoffice")),
    ("library", ("bibliothek", "bücher", "buecher")),
    ("wardrobe", ("ankleide", "schrank", "garderobe")),
    ("hallway", ("flur", "diele", "eingang", "treppe", "treppenhaus")),
    ("basement", ("keller", "untergeschoss")),
    ("storage", ("lager", "abstell", "speicher", "vorrat", "kammer")),
    ("garden", ("garten", "rasen", "hof")),
    ("garden_bed", ("beet", "gemüse", "gemuese", "kräuter", "kraeuter")),
    ("balcony", ("balkon", "loggia")),
    ("terrace", ("terrasse",)),
    ("property", ("grundstück", "grundstueck")),
    ("work", ("arbeit", "firma")),
    ("school", ("schule", "schul")),
    ("doctor", ("arzt", "praxis", "klinik")),
    ("shopping", ("einkauf", "einkaufen")),
    ("shop", ("geschäft", "geschaeft", "laden")),
    ("authority", ("behörde", "behoerde", "amt")),
    ("bank", ("bank",)),
    ("post_office", ("post",)),
    ("beach", ("strand",)),
    ("camping", ("camping",)),
    ("hotel", ("hotel",)),
    ("dog", ("hund",)),
    ("cat", ("katze",)),
    ("pets", ("haustier", "haustiere", "tier")),
    ("aquarium", ("aquarium",)),
    ("chicken_coop", ("hühner", "huehner", "hühnerstall", "huehnerstall")),
    ("stable", ("stall", "pferd")),
    ("gym", ("fitness", "sport")),
    ("atelier", ("atelier",)),
    ("gaming", ("gaming", "spiel")),
    ("wine_cellar", ("weinkeller",)),
    ("home_bar", ("bar", "hausbar")),
    ("sewing", ("nähen", "naehen", "nähzimmer", "naehzimmer")),
)

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
    "camera":    '<path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/>',
    "vacuum":    '<circle cx="9" cy="13" r="5"/><path d="M14 13h4l2-4V7h-6"/><line x1="9" y1="18" x2="9" y2="21"/>',
    "trash_bin": '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6m5 0V4h4v2m-3 4v6m4-6v6"/>',
    "plant":     '<path d="M12 22V12"/><path d="M12 12C12 7 7 5 7 5s1 5 5 7"/><path d="M12 12c0-5 5-7 5-7s-1 5-5 7"/>',
    "box":       '<path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
    "hanger":    '<path d="M20.38 18.57L12 13 3.62 18.57A2 2 0 005 22h14a2 2 0 001.38-3.43z"/><path d="M12 13V7"/><circle cx="12" cy="5" r="2"/>',
    "broom":     '<path d="M8 19l-5 2 2-5L16 5l3 3L8 19z"/><path d="M16 5l3 3"/>',
    "drop":      '<path d="M12 2.69l5.66 5.66a8 8 0 11-11.31 0z"/>',
    "star":      '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "archive":   '<polyline points="21 8 21 21 3 21 3 8"/><rect x="1" y="3" width="22" height="5"/><line x1="10" y1="12" x2="14" y2="12"/>',
    "clock":     '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "pause":     '<rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>',
    "download":  '<path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>',
    "alert":     '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "flag":      '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"/><line x1="4" y1="22" x2="4" y2="15"/>',
    "settings":  '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/>',
}

# Navigation items: (openmoji filename, label, page_key, href)
_NAV_ITEMS = [
    ("1F3E0", "Zuhause",  "home",     "./"),
    ("1F9F9", "Aufgaben", "tasks",    "tasks"),
    ("1F4E6", "Projekte", "projects", "projects"),
    ("1F4A1", "Punkte",   "scores",   "scores"),
    ("1F527", "Ich",      "settings", "settings"),
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


def _openmoji_nav_icon(filename: str, label: str) -> str:
    """Small local OpenMoji image for the bottom navigation."""
    return (
        f'<img class="nav-openmoji" src="assets/icons/{filename}.svg" '
        f'width="24" height="24" alt="" aria-hidden="true" '
        f'title="{escape(label)}" loading="lazy">'
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


def _task_icon(name: str, room: str = "", size: int = 44, icon: str = "") -> str:
    """Round icon bubble using OpenMoji SVG for a task."""
    key = icon if (icon and icon in _TASK_ICONS) else _task_icon_key(name, room)
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


# Human-readable labels for each icon key shown in the chooser
_ICON_LABELS: dict[str, str] = {
    "besen": "Fegen", "schwamm": "Schrubben", "putzen": "Putzen",
    "eimer": "Wischen", "dusche": "Dusche", "bad": "Badewanne",
    "toilette": "Toilette", "papier": "Klopapier", "kochen": "Kochen",
    "abwasch": "Abwasch", "kuehlschrank": "Kühlschrank", "lunchbox": "Lunchbox",
    "waesche": "Wäsche", "buegeln": "Bügeln", "pflanze": "Pflanze",
    "garten": "Garten", "laub": "Laub", "saen": "Säen",
    "schnee": "Schnee", "blumen": "Blumen", "muell": "Müll",
    "recycling": "Recycling", "einkaufen": "Einkaufen", "post": "Post",
    "tier": "Haustier", "hund": "Hund", "katze": "Katze",
    "werkzeug": "Werkzeug", "schraube": "Reparatur", "gluehbirne": "Glühbirne",
    "batterie": "Batterie", "schluessel": "Schlüssel", "buecher": "Lernen",
    "rucksack": "Schule", "medizin": "Medizin", "bett": "Bett machen",
    "fenster": "Fenster", "bad_auffuel": "Bad auffüllen", "lager": "Lager",
    "auto": "Auto", "tanken": "Tanken", "heizung": "Heizung",
    "default": "Allgemein",
}


def _icon_chooser(current_key: str = "", input_name: str = "icon",
                  include_room_icons: bool = False) -> str:
    """Icon-Chooser grid für Aufgaben- und Projekt-Formulare."""
    items = ""
    for key, (filename, bg) in _TASK_ICONS.items():
        active = ' active' if key == current_key else ''
        label = _ICON_LABELS.get(key, key)
        items += (
            f'<button type="button" class="icon-choice{active}" data-key="{key}"'
            f' data-label="{label.casefold()} {key}" title="{label}"'
            f' onclick="pickIcon(this,\'{input_name}\')">'
            f'<img src="assets/icons/{filename}.svg" width="26" height="26"'
            f' style="display:block">'
            f'</button>'
        )
    if include_room_icons:
        for key, (filename, bg) in ROOM_ICON_CHOICES.items():
            active = ' active' if key == current_key else ''
            label = ROOM_ICON_LABELS.get(key, key)
            items += (
                f'<button type="button" class="icon-choice{active}" data-key="{key}"'
                f' data-label="{label.casefold()} {key}" title="{label}"'
                f' onclick="pickIcon(this,\'{input_name}\')">'
                f'<img src="assets/icons/{filename}.svg" width="26" height="26"'
                f' style="display:block">'
                f'</button>'
            )
    auto_active = ' active' if not current_key else ''
    auto_btn = (
        f'<button type="button" class="icon-choice{auto_active}" data-key=""'
        f' data-label="automatisch auto"'
        f' title="Automatisch" onclick="pickIcon(this,\'{input_name}\')"'
        f' style="font-size:1.1rem">🔮</button>'
    )
    js = """<script>
function pickIcon(el,name){
  el.closest('.icon-chooser').querySelectorAll('.icon-choice')
    .forEach(function(e){e.classList.remove('active')});
  el.classList.add('active');
  document.getElementById('icon-input-'+name).value=el.dataset.key;
}
function filterIcons(input){
  var query=(input.value||'').trim().toLowerCase();
  var root=input.closest('.form-group');
  root.querySelectorAll('.icon-choice').forEach(function(btn){
    var label=(btn.dataset.label||'').toLowerCase();
    btn.style.display=(!query || label.indexOf(query)!==-1) ? '' : 'none';
  });
}
</script>"""
    return (
        f'<div class="form-group">'
        f'<label>Icon <span class="muted" style="font-weight:400;font-size:0.75rem">'
        f'— optional, wird sonst automatisch erkannt</span></label>'
        f'<div class="icon-filter"><input type="search" placeholder="Icon suchen" '
        f'oninput="filterIcons(this)" autocomplete="off"></div>'
        f'<div class="icon-chooser">{auto_btn}{items}</div>'
        f'<input type="hidden" name="{input_name}" id="icon-input-{input_name}"'
        f' value="{current_key}">'
        f'</div>'
        f'{js}'
    )


def _proj_icon(room: str = "", size: int = 46, icon: str = "") -> str:
    """Round icon bubble for a project — uses OpenMoji like task icons."""
    if icon and icon in ROOM_ICON_CHOICES:
        filename, bg = ROOM_ICON_CHOICES[icon]
    elif icon and icon in _TASK_ICONS:
        filename, bg = _TASK_ICONS[icon]
    else:
        filename, bg = _auto_room_icon_config(room)
    img_size = int(size * 0.62)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:{bg};display:flex;align-items:center;'
        f'justify-content:center;flex-shrink:0;overflow:hidden">'
        f'<img src="assets/icons/{filename}.svg" width="{img_size}" height="{img_size}"'
        f' style="display:block" loading="lazy">'
        f'</div>'
    )


def _auto_room_icon_config(room: str) -> tuple[str, str]:
    room_name = (room or "").casefold()
    for key, aliases in ROOM_ICON_ALIASES:
        if any(alias in room_name for alias in aliases):
            return ROOM_ICON_CHOICES[key]
    return ROOM_ICONS.get(room, ROOM_ICON_CHOICES["home"])


def _room_icon(room: str, size: int = 40,
               stored: dict[str, str] | None = None) -> str:
    """Round icon bubble using OpenMoji SVG for a room.
    stored: optional {room_name: icon_key} overrides from DB."""
    if stored and room in stored and stored[room] in ROOM_ICON_CHOICES:
        filename, bg = ROOM_ICON_CHOICES[stored[room]]
    elif stored and room in stored and stored[room] in _TASK_ICONS:
        filename, bg = _TASK_ICONS[stored[room]]
    else:
        filename, bg = _auto_room_icon_config(room)
    img_size = int(size * 0.60)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'background:{bg};display:flex;align-items:center;'
        f'justify-content:center;flex-shrink:0;overflow:hidden">'
        f'<img src="assets/icons/{filename}.svg" width="{img_size}" height="{img_size}"'
        f' style="display:block" loading="lazy">'
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
    if days <= 0:
        return "Einmalig"
    return INTERVALS.get(days, f"Alle {days} Tage")


def urgency_class(days: int) -> str:
    if days < 0:  return "overdue"
    if days == 0: return "today"
    if days <= 3: return "soon"
    return "ok"


def _base(request: Request) -> str:
    path = request.headers.get("X-Ingress-Path", "").rstrip("/")
    return path + "/"


def _ha_user(request: Request) -> str:
    return (
        request.headers.get("X-Remote-User-Display-Name") or
        request.headers.get("X-Remote-User-Name", "")
    ).strip()


def person_suffix(person: str = "", separator: str = "?") -> str:
    return f"{separator}p={quote(person)}" if person else ""


def resolve_person(request: Request, p_param: str = "") -> str:
    ha_user = _ha_user(request)
    if p_param and ha_user in get_admins():
        return p_param
    return ha_user or p_param


def _selected(value, current) -> str:
    return " selected" if str(value) == str(current) else ""


def format_date_de(raw: str) -> str:
    if not raw:
        return ""
    try:
        return date.fromisoformat(raw).strftime("%d.%m.%Y")
    except ValueError:
        return raw


def _comment_time(raw: str) -> str:
    try:
        return datetime.fromisoformat(raw).strftime("%d.%m.%Y %H:%M")
    except ValueError:
        return raw[:16].replace("T", " ")


def comments_card(entity_type: str, entity_id: str, action: str,
                  person: str = "", margin_top: bool = False) -> str:
    comments = list_comments(entity_type, entity_id)
    total = len(comments)
    if comments:
        rows = ""
        for c in comments:
            author = escape(c.author or "Unbekannt")
            text = escape(c.text).replace("\n", "<br>")
            created = escape(_comment_time(c.created_at))
            rows += f"""
            <div class="task-row" style="align-items:flex-start">
              <div class="task-body">
                <div class="task-header">
                  <span class="task-name">{author}</span>
                  <span class="task-meta">{created}</span>
                </div>
                <div class="muted" style="margin-top:0.25rem;line-height:1.45">{text}</div>
              </div>
            </div>"""
    else:
        rows = (
            '<div class="comments-empty">'
            '<div style="font-weight:600">Noch keine Notizen</div>'
            '<div class="muted" style="font-size:0.8rem;margin-top:0.2rem">'
            'Halte Hinweise oder Absprachen direkt hier fest.</div>'
            '</div>'
        )

    margin = "margin-top:1rem;" if margin_top else "margin-bottom:1rem;"
    open_attr = " open" if total else ""
    count_label = f"{total} Notiz{'en' if total != 1 else ''}" if total else "Keine Notizen"
    return f"""
    <details class="card comments-card" style="{margin}"{open_attr}>
      <summary class="comments-head">
        <div>
          <h3>Notizen</h3>
          <div class="muted">{count_label} · Hinweise und Absprachen</div>
        </div>
        <span class="comment-summary-icon">{_icon("edit", 15)}</span>
      </summary>
      {rows}
      <form class="comment-form" method="post" action="{action}">
        <input type="hidden" name="return_p" value="{person}">
        <div class="form-group">
          <label>Neue Notiz</label>
          <textarea name="text" rows="3" required placeholder="Hinweis oder Kommentar"></textarea>
        </div>
        <button class="btn btn-primary btn-sm" type="submit">Notiz speichern</button>
      </form>
    </details>"""


def photos_card(entity_type: str, entity_id: str, action: str,
                person: str = "", title: str = "Fotos",
                margin_top: bool = False) -> str:
    photos = list_photos(entity_type, entity_id)
    total = len(photos)
    safe_id = "".join(ch if ch.isalnum() else "-" for ch in f"{entity_type}-{entity_id}")
    live_input_id = escape(f"photo-live-{safe_id}")
    camera_input_id = escape(f"photo-camera-{safe_id}")
    file_input_id = escape(f"photo-file-{safe_id}")
    sections = {"before": "", "after": ""}
    for photo in photos:
        ptype = photo.get("photo_type") if photo.get("photo_type") in sections else "before"
        label = "Vorher" if ptype == "before" else "Nachher"
        filename = escape(photo.get("filename", ""))
        photo_id = escape(photo.get("id", ""))
        sections[ptype] += f"""
        <figure class="photo-tile">
          <img src="photos/{filename}" alt="{label}">
          <figcaption>
            <span>{label}</span>
            <a class="photo-delete" href="{action}/{photo_id}/delete{person_suffix(person)}"
               onclick="return confirm('Foto löschen?')" title="Foto löschen">
              {_icon("trash", 13)}
            </a>
          </figcaption>
        </figure>"""

    def _section(label: str, key: str) -> str:
        body = sections[key] or '<div class="photo-empty">Noch kein Foto</div>'
        return f"""
        <div class="photo-section">
          <div class="photo-section-title">{label}</div>
          <div class="photo-grid">{body}</div>
        </div>"""

    margin = "margin-top:1rem;" if margin_top else "margin-bottom:1rem;"
    open_attr = " open" if total else ""
    count_label = f"{total} Foto{'s' if total != 1 else ''}" if total else "Keine Fotos"
    return f"""
    <details class="card photos-card" style="{margin}"{open_attr}>
      <summary class="photos-head">
        <div>
          <h3>{title}</h3>
          <div class="muted">{count_label} · Vorher/Nachher dokumentieren</div>
        </div>
        <span class="photo-summary-icon">{_icon("camera", 15)}</span>
      </summary>
      {_section("Vorher", "before")}
      {_section("Nachher", "after")}
      <form class="photo-upload" method="post" action="{action}" enctype="multipart/form-data">
        <input type="hidden" name="return_p" value="{person}">
        <div class="photo-type-picker">
          <label class="option-card">
            <input type="radio" name="photo_type" value="before" checked>
            <span>Vorher</span>
          </label>
          <label class="option-card">
            <input type="radio" name="photo_type" value="after">
            <span>Nachher</span>
          </label>
        </div>
        <input id="{live_input_id}" class="photo-file-input photo-live-input" type="file"
               name="photo" accept="image/*">
        <input id="{camera_input_id}" class="photo-file-input" type="file"
               name="photo_camera" accept="image/*,android/force-camera-workaround"
               capture="environment" onchange="this.form.submit()">
        <input id="{file_input_id}" class="photo-file-input" type="file"
               name="photo_file" accept="image/*" onchange="this.form.submit()">
        <div class="photo-actions">
          <label class="btn btn-ghost btn-sm camera-native-button" for="{camera_input_id}">
            {_icon("camera", 14)} Kamera öffnen
          </label>
          <button class="btn btn-ghost btn-sm camera-start" type="button" hidden>
            {_icon("camera", 14)} Kamera öffnen
          </button>
          <label class="btn btn-outline btn-sm photo-file-button" for="{file_input_id}">
            {_icon("plus", 14)} Datei auswählen
          </label>
        </div>
        <div class="camera-panel" hidden>
          <video class="camera-preview" playsinline autoplay muted></video>
          <div class="camera-actions">
            <button class="btn btn-primary btn-sm camera-shot" type="button">
              {_icon("camera", 14, "white")} Aufnehmen
            </button>
            <button class="btn btn-ghost btn-sm camera-stop" type="button">Schließen</button>
          </div>
        </div>
        <div class="camera-msg muted"></div>
        <div class="muted photo-upload-hint">Kamera öffnet die Aufnahme. Datei auswählen lädt ein vorhandenes Foto hoch.</div>
      </form>
    </details>"""


def task_row(task, base: str = "", person: str = "", show_assigned: bool = False,
             paused: bool = False, vacation_until: str = "") -> str:
    from reminders import task_reminder_recipients

    effort_labels = {"low": "Wenig", "medium": "Mittel", "high": "Viel"}
    effort_badges = {"low": "ok", "medium": "today", "high": "overdue"}
    due = task.days_until_due()

    if due < 0:
        badge_text, badge_cls = "Überfällig", "overdue"
        date_text = f"{abs(due)}d überfällig"
    elif due == 0:
        badge_text, badge_cls = "Heute", "today"
        date_text = "Heute"
    else:
        badge_text, badge_cls = "Geplant", "ok"
        date_text = "Morgen" if due == 1 else f"In {due} Tagen"

    if task.snooze_until:
        try:
            snooze_d = date.fromisoformat(task.snooze_until)
            if snooze_d > date.today():
                date_text = f"Verschoben bis {snooze_d.strftime('%-d. %b')}"
                badge_text, badge_cls = "Verschoben", "ok"
        except ValueError:
            pass

    task_paused = bool(paused or getattr(task, "is_paused", lambda: False)())
    pause_until = getattr(task, "pause_until", "") or vacation_until
    pause_reason = getattr(task, "pause_reason", "") or ""

    if task_paused:
        badge_text, badge_cls = "Pausiert", "ok"
        date_text = (
            f"Pausiert bis {format_date_de(pause_until)}"
            if pause_until else "Pausiert"
        )
        if pause_reason:
            date_text += f" · {pause_reason}"

    important_cls = " important" if task.important else ""
    paused_cls = " is-paused" if task_paused else ""
    star = _icon("star", 13, "var(--warning)", 2.5) if task.important else ""
    effort_badge = (
        f'<span class="badge {effort_badges[task.effort]}" '
        f'style="font-size:0.62rem;flex-shrink:0">{effort_labels[task.effort]}</span>'
    ) if task.effort in effort_labels else ""
    sub_badges = (
        f'<div class="task-badge-subrow">{effort_badge}</div>'
        if effort_badge else ""
    )
    assigned_txt = ""
    if task.assigned_to and show_assigned:
        assigned_txt = (
            f'<span class="task-meta" style="font-size:0.72rem">'
            f'→ {", ".join(task.assigned_to)}</span>'
        )
    task_meta_inline = f'<span class="task-name-meta"> · {date_text}</span>'
    photo_count = count_photos("task", task.id)
    photo_badge = (
        f'<span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    psuffix = person_suffix(person)

    done_btn = (
        f'<form class="inline" method="post" action="{base}tasks/{task.id}/done">'
        + (f'<input type="hidden" name="done_by" value="{person}">' if person else "")
        + (f'<input type="hidden" name="return_p" value="{person}">' if person else "")
        + f'<button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>'
        f'</form>'
    )
    snooze_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/snooze{psuffix}" '
        f'title="Verschieben">{_icon("clock", 16)}</a>'
    )
    pause_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/pause{psuffix}" '
        f'title="Pause bearbeiten">{_icon("pause", 15)}</a>'
    )
    remind_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/remind{psuffix}" '
        f'title="Andere erinnern">{_icon("bell", 16)}</a>'
    ) if task_reminder_recipients(task, person) else ""
    edit_btn = (
        f'<a class="icon-btn" href="{base}tasks/{task.id}/edit{psuffix}" title="Bearbeiten">'
        f'{_icon("edit", 16)}</a>'
    )
    del_btn = (
        f'<a class="icon-btn danger" href="{base}tasks/{task.id}/delete{psuffix}" '
        f'onclick="return confirm(\'Aufgabe löschen?\')" title="Löschen">'
        f'{_icon("trash", 16)}</a>'
    )

    return f"""
    <div class="task-row{important_cls}{paused_cls}">
      {_task_icon(task.name, task.room, icon=task.icon, size=40)}
      <div class="task-body">
        <div class="task-header">
          <span class="task-name">{star}{task.name}{task_meta_inline}</span>
          <div class="task-badges">
            <span class="badge {badge_cls}">{badge_text}</span>
            {sub_badges}
          </div>
        </div>
        {f'<div class="task-date">{assigned_txt}{photo_badge}</div>' if assigned_txt or photo_badge else ''}
      </div>
      <div class="task-actions">
        {done_btn}{snooze_btn}{pause_btn}{remind_btn}{edit_btn}{del_btn}
      </div>
    </div>"""


def project_row(project, visible_steps: list, all_steps: list, person: str = "",
                grouped_by_person: bool = False, person_name: str = "") -> str:
    done, total = project.progress(visible_steps)
    pct = int(done / total * 100) if total else 0
    assigned = (
        f"<span>→ {project.assigned_to}</span>"
        if project.assigned_to and not grouped_by_person else ""
    )
    fill_class = "green" if project.completed else ""
    opacity = "opacity:0.65;" if project.completed else ""
    detail_suffix = (
        f"?scope=people{person_suffix(person, '&')}"
        if grouped_by_person else person_suffix(person)
    )
    person_hint = f" · {person_name}" if person_name else ""
    status_badge = (
        '<span class="badge ok">Abgeschlossen</span>'
        if project.completed else f'<span class="badge today">{done}/{total}</span>'
    )
    project_photo_count = count_photos("project", project.id)
    step_photo_count = sum(count_photos("step", step.id) for step in all_steps)
    photo_count = project_photo_count + step_photo_count
    photo_hint = (
        f'<span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    reference_person = person_name or person
    foreign_open_assignees: list[str] = []
    for step in all_steps:
        assignee = step.assigned_to or project.assigned_to or ""
        if step.completed or not assignee or assignee == reference_person:
            continue
        if assignee not in foreign_open_assignees:
            foreign_open_assignees.append(assignee)
    foreign_open_count = sum(
        1
        for step in all_steps
        if not step.completed
        and (step.assigned_to or project.assigned_to or "")
        and (step.assigned_to or project.assigned_to or "") != reference_person
    )
    if foreign_open_count:
        shown_names = ", ".join(escape(name) for name in foreign_open_assignees[:2])
        more = f" +{len(foreign_open_assignees) - 2}" if len(foreign_open_assignees) > 2 else ""
        foreign_hint = (
            f'<span class="proj-reminder-hint">{_icon("bell", 13)} '
            f'{foreign_open_count} offen bei {shown_names}{more}</span>'
        )
    else:
        foreign_hint = ""

    if project.completed:
        action_btns = (
            f'<a class="icon-btn" href="projects/{project.id}/archive{person_suffix(person)}" '
            f'title="Archivieren">{_icon("archive", 16)}</a>'
        )
    else:
        action_btns = (
            f'<a class="icon-btn" href="projects/{project.id}/edit{person_suffix(person)}" '
            f'title="Bearbeiten">{_icon("edit", 16)}</a>'
        )
    del_btn = (
        f'<a class="icon-btn danger" href="projects/{project.id}/delete{person_suffix(person)}" '
        f'onclick="return confirm(\'Projekt löschen?\')" title="Löschen">'
        f'{_icon("trash", 16)}</a>'
    )

    return f"""
    <div class="proj-row" style="{opacity}">
      <a href="projects/{project.id}{detail_suffix}" style="display:contents;text-decoration:none">
        {_proj_icon(project.room, icon=project.icon)}
      </a>
      <div class="proj-main">
        <div class="proj-head">
          <a class="proj-title" href="projects/{project.id}{detail_suffix}">{project.name}</a>
          {status_badge}
        </div>
        <div class="proj-meta">
          <span>{project.room}{person_hint}</span>
          <span>{len(all_steps)} Schritte</span>
          {assigned}
          {photo_hint}
          {foreign_hint}
        </div>
        <div class="proj-progress">
          <div class="progress-track">
            <div class="progress-fill {fill_class}" style="width:{pct}%"></div>
          </div>
          <span class="proj-percent">{pct}%</span>
        </div>
      </div>
      <div class="task-actions">{action_btns}{del_btn}</div>
    </div>"""


def project_step_row(project, step, assignee: str, person_options: str,
                     base: str, person: str = "") -> str:
    psuffix = person_suffix(person)
    photo_count = count_photos("step", step.id)
    photo_hint = (
        f' · <span class="task-photo-badge" title="{photo_count} Foto'
        f'{"s" if photo_count != 1 else ""}">{_icon("camera", 12)} {photo_count}</span>'
        if photo_count else ""
    )
    if step.completed:
        who = f" · {step.completed_by}" if step.completed_by else ""
        return f"""
        <div class="project-step-row is-done">
          <span style="color:var(--success);font-size:1.1rem;flex-shrink:0">
            {_icon("check", 18, "var(--success)")}
          </span>
          <div class="project-step-main">
            <span class="project-step-title">{step.name}</span>
            <span class="project-step-meta">{step.points} Pkt · → {assignee or "Niemand"}{who}{photo_hint}</span>
          </div>
        </div>"""

    remind_btn = (
        f'<a class="icon-btn" href="{base}projects/{project.id}/steps/{step.id}/remind{psuffix}" '
        f'title="Andere erinnern">{_icon("bell", 16)}</a>'
    ) if assignee and assignee != person else ""

    return f"""
    <div class="project-step-row">
      <div class="project-step-main">
        <span class="project-step-title">{step.name}</span>
        <span class="project-step-meta">{step.points} Pkt{photo_hint}</span>
      </div>
      <div class="project-step-actions">
        <form class="project-step-form" method="post" action="{base}projects/{project.id}/steps/{step.id}/assign">
          <input type="hidden" name="return_p" value="{person}">
          <select class="project-step-person" name="assigned_to" aria-label="Zugewiesen an"
                  onchange="this.form.submit()">
          {person_options}
          </select>
        </form>
        <form class="inline" method="post" action="{base}projects/{project.id}/steps/{step.id}/done">
          <input type="hidden" name="done_by" value="{assignee}">
          <input type="hidden" name="return_p" value="{person}">
          <button class="icon-btn success" title="Erledigt">{_icon("check", 17)}</button>
        </form>
        {remind_btn}
        <a class="icon-btn danger"
           href="{base}projects/{project.id}/steps/{step.id}/delete{psuffix}"
           onclick="return confirm('Schritt löschen?')"
           title="Schritt löschen">
           {_icon("trash", 15)}
        </a>
      </div>
    </div>"""


def project_step_reminder_form(project, step, assignee: str, base: str,
                               person: str = "") -> str:
    default_message = f"Kannst du bitte an {step.name} denken?"
    psuffix = person_suffix(person)
    return f"""
    <div class="page-header">
      <h2>Erinnerung senden</h2>
      <a class="icon-btn" href="{base}projects/{project.id}{psuffix}" title="Abbrechen">{_icon("chevron_l", 20)}</a>
    </div>
    <div class="card" style="margin-bottom:0.75rem">
      <div style="font-weight:600;margin-bottom:0.2rem">{project.name}</div>
      <div class="task-meta">{step.name} · {assignee}</div>
    </div>
    <div class="card">
      <form method="post" action="{base}projects/{project.id}/steps/{step.id}/remind">
        <input type="hidden" name="return_p" value="{person}">
        <div class="form-group">
          <label>Erinnerung an</label>
          <div style="padding:0.7rem 0.8rem;border:1px solid var(--border);
                      border-radius:8px;background:var(--bg-soft);font-weight:600">
            {assignee}
          </div>
        </div>
        <div class="form-group">
          <label>Nachricht</label>
          <textarea name="message" rows="3" required>{escape(default_message)}</textarea>
        </div>
        <button class="btn btn-primary btn-full" type="submit">Erinnerung senden</button>
        <a class="btn btn-ghost btn-full" href="{base}projects/{project.id}{psuffix}"
           style="margin-top:0.5rem">Abbrechen</a>
      </form>
    </div>"""


def render(content: str, request: Request, page: str = "home",
           person: str = "") -> HTMLResponse:
    base = _base(request)
    psuffix = person_suffix(person)
    admins = get_admins()
    ha_user = _ha_user(request)
    is_admin = ha_user in admins
    display_person = person or ha_user
    vacation_banner = ""
    flash = ""
    msg = request.query_params.get("msg", "").strip()
    if msg:
        flash = (
            '<div class="card" style="border-color:var(--success);'
            'background:var(--success-bg);margin-bottom:1rem">'
            f'<div style="font-weight:750;color:var(--success)">{escape(msg)}</div>'
            '</div>'
        )
    if display_person and is_vacation_mode_active(display_person):
        vacation = get_vacation_mode(display_person)
        until = vacation.get("until") or ""
        until_txt = f" bis {format_date_de(until)}" if until else ""
        vacation_banner = (
            '<div class="card" style="border-color:var(--warning);'
            'background:var(--warning-bg);margin-bottom:1rem">'
            f'<div style="font-weight:750;color:var(--warning)">Urlaubsmodus aktiv{until_txt}</div>'
            '<div class="muted" style="margin-top:0.25rem;font-size:0.82rem">'
            'Fällige Aufgaben und tägliche Benachrichtigungen sind pausiert.</div>'
            '</div>'
        )

    # Person nav pill / dropdown
    if not display_person:
        person_nav = f'<a href="{base}settings" class="h-pill">Wer bin ich?</a>'
    elif is_admin:
        profile_person = person or ha_user
        viewing_other = bool(ha_user and profile_person != ha_user)
        menu_hint = (
            f'Ansicht von {profile_person}'
            if viewing_other else
            'Meine Ansicht'
        )
        own_link = (
            f'<a href="{base}" class="hpill-action">{_icon("home", 16)}<span>Zurück zu meiner Ansicht</span></a>'
            if viewing_other else ""
        )
        current_profile = (
            f'<a href="{base}settings{person_suffix(profile_person)}" class="hpill-action">'
            f'{_icon("settings", 16)}<span>Einstellungen für {profile_person}</span></a>'
        )
        own_profile = (
            f'<a href="{base}settings{person_suffix(ha_user)}" class="hpill-action">'
            f'{_icon("person", 16)}<span>Meine Einstellungen</span></a>'
            if viewing_other else ""
        )
        person_nav = f'''
        <details class="hpill-menu">
          <summary class="h-pill h-pill-person">
            {_icon("person", 15)}
            <span>{display_person}</span>
            <span class="h-pill-caret">▾</span>
          </summary>
          <div class="hpill-dropdown">
            <div class="hpill-head">
              <div class="hpill-head-label">{menu_hint}</div>
              <div class="hpill-head-name">{display_person}</div>
            </div>
            <div class="hpill-section-label">Ansicht</div>
            {own_link}
            <a href="{base}settings" class="hpill-action">{_icon("person", 16)}<span>Person wechseln</span></a>
            <div class="hpill-section-label">Einstellungen</div>
            {own_profile}
            {current_profile}
            <div class="hpill-section-label">Haushaltshilfen</div>
            <a href="{base}housekeeping" class="hpill-action">{_icon("clock", 16)}<span>Arbeitszeiten verwalten</span></a>
            <div class="hpill-section-label">Verwaltung</div>
            <a href="{base}admin" class="hpill-action">{_icon("settings", 16)}<span>Admin-Bereich</span></a>
          </div>
        </details>'''
    else:
        person_nav = (
            f'<a href="{base}settings{person_suffix(display_person)}" class="h-pill h-pill-person">'
            f'{_icon("person", 15)}<span>{display_person}</span></a>'
        )

    # Bottom navigation with local OpenMoji icons
    nav_items = ""
    for icon_file, label, page_key, href in _NAV_ITEMS:
        active = "active" if page == page_key else ""
        nav_items += (
            f'<a href="{href}{psuffix}" class="nav-item {active}">'
            f'{_openmoji_nav_icon(icon_file, label)}'
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
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{background:#f4f0f2;color:#24181f;
             font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
             padding-bottom:5rem}}
  body{{opacity:0}}
  header{{background:rgba(255,255,255,0.90);border-bottom:1px solid #ddd6da;
          padding:0.75rem 1rem;display:flex;align-items:center;
          justify-content:space-between;position:sticky;top:0;z-index:10}}
  .bottom-nav{{position:fixed;bottom:0;left:0;right:0;height:4.25rem;
               background:rgba(255,255,255,0.96);border-top:1px solid #ddd6da;
               display:flex;z-index:10;overflow:hidden}}
  .nav-item{{flex:1;display:flex;flex-direction:column;align-items:center;
             justify-content:center;text-decoration:none;color:transparent}}
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
  </div>
</header>
<main>
        {flash}
        {vacation_banner}
        {content}
      </main>
<nav class="bottom-nav">{nav_items}</nav>
<script>
(function(){{
  function selectedPhotoType(card){{
    var selected = card.querySelector('input[name="photo_type"]:checked');
    return selected ? selected.value : 'before';
  }}

  function setCameraMessage(card, text){{
    var msg = card.querySelector('.camera-msg');
    if (msg) msg.textContent = text || '';
  }}

  async function stopCamera(card){{
    var stream = card._cameraStream;
    if (stream) stream.getTracks().forEach(function(track){{ track.stop(); }});
    card._cameraStream = null;
    var panel = card.querySelector('.camera-panel');
    if (panel) panel.hidden = true;
  }}

  function waitForVideo(video){{
    if (video.videoWidth && video.videoHeight) return Promise.resolve();
    return new Promise(function(resolve){{
      var done = function(){{
        clearTimeout(timer);
        video.removeEventListener('loadedmetadata', done);
        video.removeEventListener('canplay', done);
        resolve();
      }};
      var timer = setTimeout(done, 1500);
      video.addEventListener('loadedmetadata', done);
      video.addEventListener('canplay', done);
    }});
  }}

  function setCameraMode(card, liveMode){{
    var nativeButton = card.querySelector('.camera-native-button');
    var liveButton = card.querySelector('.camera-start');
    if (nativeButton) nativeButton.hidden = !!liveMode;
    if (liveButton) liveButton.hidden = !liveMode;
  }}

  function enhanceCameraControls(){{
    var liveMode = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    document.querySelectorAll('.photos-card').forEach(function(card){{
      setCameraMode(card, liveMode);
    }});
  }}

  function markPendingPhoto(card, input){{
    if (!card || !card.classList.contains('photo-pending-card')) return;
    card.querySelectorAll('.photo-file-input').forEach(function(other){{
      if (other !== input) other.value = '';
    }});
    var filename = input && input.files && input.files.length ? input.files[0].name : '';
    card.classList.toggle('has-pending-photo', !!filename);
    setCameraMessage(card, filename ? 'Vorher-Foto ausgewählt: ' + filename : '');
  }}

  async function startCamera(card){{
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
      setCameraMode(card, false);
      setCameraMessage(card, 'Live-Kamera nicht verfügbar. Nutze Kamera öffnen oder Datei auswählen als Fallback.');
      return;
    }}
    try {{
      await stopCamera(card);
      var stream = await navigator.mediaDevices.getUserMedia({{
        video: {{ facingMode: {{ ideal: 'environment' }} }},
        audio: false
      }});
      card._cameraStream = stream;
      var video = card.querySelector('.camera-preview');
      var panel = card.querySelector('.camera-panel');
      video.srcObject = stream;
      panel.hidden = false;
      setCameraMessage(card, '');
    }} catch (err) {{
      setCameraMode(card, false);
      setCameraMessage(card, 'Live-Kamera wurde blockiert. Kamera öffnen nutzt jetzt den nativen Kamera-/Dateidialog.');
    }}
  }}

  async function snapshotBlob(video){{
    await waitForVideo(video);
    return new Promise(function(resolve){{
      var canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 1280;
      canvas.height = video.videoHeight || 960;
      canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
      canvas.toBlob(function(blob){{ resolve(blob); }}, 'image/jpeg', 0.9);
    }});
  }}

  async function uploadBlob(card, blob){{
    var pending = card.classList.contains('photo-pending-card');
    var form = card.querySelector('.photo-upload') || card.closest('form');
    var input = card.querySelector('.photo-live-input');
    if (!form || !input || !blob) return;

    if (window.File && window.DataTransfer) {{
      var file = new File([blob], 'camera.jpg', {{ type: 'image/jpeg' }});
      var transfer = new DataTransfer();
      transfer.items.add(file);
      input.files = transfer.files;
      await stopCamera(card);
      if (pending) {{
        markPendingPhoto(card, input);
        return;
      }}
      form.submit();
      return;
    }}

    if (pending) {{
      await stopCamera(card);
      setCameraMessage(card, 'Live-Foto konnte nicht übernommen werden. Bitte Kamera öffnen oder Datei auswählen nutzen.');
      return;
    }}

    var data = new FormData();
    data.append('photo_type', selectedPhotoType(card));
    var returnP = form.querySelector('input[name="return_p"]');
    if (returnP) data.append('return_p', returnP.value);
    data.append('photo', blob, 'camera.jpg');

    var response = await fetch(form.action, {{
      method: 'POST',
      body: data,
      credentials: 'same-origin'
    }});
    if (!response.ok && !response.redirected) throw new Error('upload failed');
    await stopCamera(card);
    window.location.href = response.url || window.location.href;
  }}

  async function takePhoto(card){{
    var video = card.querySelector('.camera-preview');
    if (!video || !video.srcObject) return;
    try {{
      setCameraMessage(card, 'Foto wird gespeichert...');
      var blob = await snapshotBlob(video);
      if (!blob) throw new Error('snapshot failed');
      await uploadBlob(card, blob);
    }} catch (err) {{
      setCameraMessage(card, 'Foto konnte nicht gespeichert werden. Bitte Datei auswählen nutzen.');
    }}
  }}

  document.addEventListener('click', function(event){{
    var start = event.target.closest('.camera-start');
    var shot = event.target.closest('.camera-shot');
    var stop = event.target.closest('.camera-stop');
    if (!start && !shot && !stop) return;
    var card = event.target.closest('.photos-card');
    if (!card) return;
    if (start) startCamera(card);
    if (shot) takePhoto(card);
    if (stop) stopCamera(card);
  }});
  document.addEventListener('change', function(event){{
    var input = event.target.closest('.photo-file-input');
    if (!input) return;
    var card = input.closest('.photos-card');
    markPendingPhoto(card, input);
  }});
  document.addEventListener('DOMContentLoaded', enhanceCameraControls);
  enhanceCameraControls();
}})();
</script>
</body>
</html>"""

    return HTMLResponse(html)
