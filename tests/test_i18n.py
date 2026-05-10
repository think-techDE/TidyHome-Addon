import sys
import unittest
from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1] / "tidyhome" / "app"
sys.path.insert(0, str(APP_DIR))

from i18n import language_options, normalize_language, resolve_language, translate_html  # noqa: E402


class I18nTests(unittest.TestCase):
    def test_language_resolution_uses_explicit_profile_language(self):
        self.assertEqual(resolve_language("es", "fr-FR,fr;q=0.9"), "es")
        self.assertEqual(normalize_language("en-US"), "en")

    def test_language_resolution_uses_accept_language_for_auto(self):
        self.assertEqual(resolve_language("auto", "fr-FR,fr;q=0.9,en;q=0.7"), "fr")
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


if __name__ == "__main__":
    unittest.main()
