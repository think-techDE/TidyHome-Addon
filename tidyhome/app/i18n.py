import re
from html import escape

from translations import MESSAGE_SOURCES, TRANSLATIONS


SUPPORTED_LANGUAGES = {
    "auto": "Automatisch",
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
    "es": "Español",
}

TARGET_LANGUAGES = {"de", "en", "fr", "es"}


def normalize_language(value: str = "") -> str:
    raw = (value or "").strip().lower().replace("_", "-")
    if not raw:
        return "de"
    if raw == "auto":
        return "auto"
    base = raw.split("-", 1)[0]
    return base if base in TARGET_LANGUAGES else "de"


def language_from_accept_header(header: str = "") -> str:
    candidates: list[tuple[float, int, str]] = []
    for index, part in enumerate((header or "").split(",")):
        pieces = [piece.strip() for piece in part.split(";") if piece.strip()]
        if not pieces:
            continue
        q = 1.0
        for param in pieces[1:]:
            if not param.startswith("q="):
                continue
            try:
                q = float(param[2:])
            except ValueError:
                q = 0.0
        candidates.append((q, index, pieces[0]))

    for q, _, token in sorted(candidates, key=lambda item: (-item[0], item[1])):
        if q <= 0:
            continue
        lang = normalize_language(token)
        if lang in TARGET_LANGUAGES:
            return lang
    return "de"


def resolve_language(setting: str = "auto", accept_language: str = "") -> str:
    lang = normalize_language(setting or "auto")
    if lang == "auto":
        return language_from_accept_header(accept_language)
    return lang


def language_options(current: str = "auto") -> str:
    selected = normalize_language(current or "auto")
    return "".join(
        # Only the automatic option is app UI; language names stay native.
        f'<option value="{escape(code, quote=True)}"'
        f'{" selected" if code == selected else ""}>'
        f'{tr("language.auto") if code == "auto" else escape(label)}</option>'
        for code, label in SUPPORTED_LANGUAGES.items()
    )


_TOKEN_RE = re.compile(r"\[\[i18n:([a-z0-9_.-]+)\]\]")


def tr(key: str) -> str:
    """Return a translation token for explicit UI text only.

    The token is resolved by translate_html() after the user's language is known.
    Free user content must not be wrapped with this helper.
    """
    return f"[[i18n:{key}]]"


def translate_key(key: str, language: str = "de") -> str:
    source = MESSAGE_SOURCES.get(key, key)
    lang = normalize_language(language)
    if lang in ("de", "auto"):
        return source
    return TRANSLATIONS.get(lang, {}).get(source, source)


def translate_html(html: str, language: str = "de") -> str:
    lang = normalize_language(language)
    return _TOKEN_RE.sub(
        lambda match: escape(translate_key(match.group(1), lang), quote=True),
        html,
    )
