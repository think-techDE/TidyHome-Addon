from html import escape

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

# Navigation items: (openmoji filename, i18n_key, page_key, href)
_NAV_ITEMS = [
    ("1F3E0", "nav.home",     "home",     "./"),
    ("1F9F9", "nav.tasks",    "tasks",    "tasks"),
    ("1F4E6", "nav.projects", "projects", "projects"),
    ("1F4A1", "nav.scores",   "scores",   "scores"),
    ("1F527", "nav.settings", "settings", "settings"),
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
