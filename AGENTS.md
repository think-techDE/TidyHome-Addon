# AGENTS.md

Kurzanleitung für KI-Agenten in diesem Repository. Ziel: schnell arbeiten, wenig Kontext verbrauchen, keine Projektkonventionen neu erraten.

## Projekt

TidyHome ist ein Home-Assistant-Add-on für Haushaltsaufgaben, Ordnungsprojekte, Punkte, Rollen und Benachrichtigungen.

Technik:
- FastAPI-App in `tidyhome/app/`
- TinyDB-Persistenz unter `/data/tidyhome.json`
- Home Assistant Ingress über Add-on-Konfiguration
- Statisches CSS in `tidyhome/assets/app.css`
- Lokale OpenMoji-SVGs in `tidyhome/assets/icons/`

## Wichtige Dateien

- `tidyhome/config.yaml`: Add-on-Metadaten und veröffentlichte Version
- `tidyhome/app/main.py`: FastAPI-App, Router, Healthcheck, interne Version
- `tidyhome/app/models.py`: Pydantic-Modelle für Aufgaben, Projekte, Schritte
- `tidyhome/app/storage.py`: TinyDB-Zugriff und Geschäftslogik
- `tidyhome/app/render.py`: HTML-Layout, Navigation, Icons, gemeinsame Render-Helfer
- `tidyhome/app/ui_cards.py`: Foto- und Notizkarten
- `tidyhome/app/ui_icons.py`: OpenMoji-/SVG-Icon-Daten und Icon-Renderer
- `tidyhome/app/i18n.py`: Sprachwahl und Token-Auflösung
- `tidyhome/app/translations/`: i18n-Quelltexte und Sprachkataloge
- `tidyhome/app/routes/dashboard.py`: Startseite und Raumansichten
- `tidyhome/app/routes/tasks.py`: Aufgabenlisten und Aufgabenformulare
- `tidyhome/app/routes/projects.py`: Projektlisten, Detailansicht und Projektformulare
- `tidyhome/app/routes/settings.py`: Einstellungen, Admin-Bereich, Raum-Icons
- `tidyhome/CHANGELOG.md`: Home-Assistant-Update-Dialog
- `README.md`, `FEATURES.md`, `ROADMAP.md`: öffentliche Projektdoku

## Arbeitsregeln

- Vor Änderungen zuerst `git status --short --branch` prüfen.
- Keine unbezogenen Änderungen zurücksetzen.
- `__pycache__` und lokale Testdaten nicht committen.
- Für manuelle Dateiänderungen `apply_patch` verwenden.
- Bei Release-Änderungen Version synchron halten:
  - `tidyhome/config.yaml`
  - `tidyhome/app/main.py`
  - README-Badge
  - `tidyhome/CHANGELOG.md`
- Bei Feature-Änderungen prüfen, ob `README.md`, `FEATURES.md` oder `ROADMAP.md` angepasst werden müssen.

## Validierung

Basisprüfung:

```powershell
& "C:\Users\Danny\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m py_compile tidyhome\app\main.py tidyhome\app\render.py tidyhome\app\routes\dashboard.py tidyhome\app\routes\tasks.py tidyhome\app\routes\projects.py tidyhome\app\routes\settings.py tidyhome\app\routes\scores.py
git diff --check
```

Bei Icon-Änderungen zusätzlich sicherstellen, dass alle referenzierten SVGs unter `tidyhome/assets/icons/` vorhanden sind.

## UI-Konventionen

- App soll ruhig, kompakt und Home-Assistant-nah wirken.
- Primäre Akzentfarbe ist Mauve/Rose, nicht als Vollflächen-Dominanz verwenden.
- Light/Dark Mode über CSS-Variablen in `app.css`.
- Touch-Ziele ausreichend groß halten.
- Aufgaben- und Raumlisten klar trennen; keine überflüssigen Aktionszeilen unter Erledigt-Buttons.
- Aufgaben-Icons kommen aus `_TASK_ICONS`.
- Raum-/Orts-Icons kommen aus `ROOM_ICON_CHOICES`.
- Projekt-Icons dürfen Aufgaben-Icons und Raum-/Orts-Icons verwenden.

## Sichtbarkeit und Rollen

- Standardansichten zeigen die Aufgaben und Projektanteile der aktuellen Person.
- Admins sehen auf dem Dashboard ebenfalls primär eigene Aufgaben.
- Admins können Raumansichten und Projektgruppen nach Personen prüfen.
- Eltern sehen eigene Aufgaben und in Raumansichten Aufgaben von Personen mit Rolle `child`.
- Nicht-Admin-Home-Assistant-Nutzer müssen die App über den Add-on-Sidebar-Eintrag sehen können (`panel_admin: false`).

## Veröffentlichung

Typischer Ablauf:

```powershell
git status --short --branch
git add README.md FEATURES.md ROADMAP.md AGENTS.md tidyhome\config.yaml tidyhome\CHANGELOG.md tidyhome\app tidyhome\assets\icons
git commit -m "Release vX.Y.Z"
git push origin main
```

Vor dem Commit prüfen, dass keine `__pycache__`-Dateien oder temporären Daten gestaged sind.
