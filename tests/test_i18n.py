import os
import sys
import tempfile
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="tidyhome-test-"))

from i18n import language_options, normalize_language, resolve_language, translate_html  # noqa: E402
from render import render  # noqa: E402
import storage  # noqa: E402


class DummyRequest:
    query_params = {}

    def __init__(self, person: str, accept_language: str = ""):
        self.headers = {"X-Remote-User-Display-Name": person}
        if accept_language:
            self.headers["accept-language"] = accept_language


class I18nTests(unittest.TestCase):
    def setUp(self):
        storage._db.drop_tables()

    def test_language_resolution_uses_explicit_profile_language(self):
        self.assertEqual(resolve_language("es", "fr-FR,fr;q=0.9"), "es")
        self.assertEqual(normalize_language("en-US"), "en")

    def test_language_resolution_uses_accept_language_for_auto(self):
        self.assertEqual(resolve_language("auto", "fr-FR,fr;q=0.9,en;q=0.7"), "fr")
        self.assertEqual(resolve_language("auto", "en;q=0.2,fr;q=0.9,es;q=0"), "fr")
        self.assertEqual(resolve_language("auto", "fr;q=0,en;q=0.5"), "en")
        self.assertEqual(resolve_language("auto", "nl-NL,nl;q=0.9"), "de")

    def test_translate_html_keeps_german_as_source_language(self):
        html = '<html lang="de"><button>Speichern</button><a>Zuhause</a>'
        self.assertEqual(translate_html(html, "de"), html)

    def test_translate_html_translates_common_navigation_and_actions(self):
        html = '<html lang="en"><button>Speichern</button><a>Zuhause</a><span>Aufgaben</span>'
        translated = translate_html(html, "en")

        self.assertIn(">Save<", translated)
        self.assertIn(">Home<", translated)
        self.assertIn(">Tasks<", translated)

    def test_language_options_marks_current_language(self):
        options = language_options("fr-FR")

        self.assertIn('value="fr" selected', options)
        self.assertIn("Français", options)

    def test_render_uses_logged_in_user_language_when_admin_views_other_person(self):
        storage.save_admins(["Ben"])
        storage.save_person_settings("Ben", [], "08:00", False, language="en")
        storage.save_person_settings("Marina", [], "08:00", False, language="fr")

        response = render("<h1>Zuhause</h1>", DummyRequest("Ben"), person="Marina")
        html = response.body.decode("utf-8")

        self.assertIn('<html lang="en">', html)
        self.assertIn(">Home<", html)
        self.assertNotIn("Accueil", html)
        self.assertEqual(response.headers["content-language"], "en")

    def test_render_auto_language_uses_request_header(self):
        storage.save_person_settings("Marina", [], "08:00", False, language="auto")

        response = render("<h1>Zuhause</h1>", DummyRequest("Marina", "es-ES,es;q=0.9"))
        html = response.body.decode("utf-8")

        self.assertIn('<html lang="es">', html)
        self.assertIn(">Inicio<", html)
        self.assertEqual(response.headers["content-language"], "es")


if __name__ == "__main__":
    unittest.main()
