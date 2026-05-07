# TidyHome – Roadmap

Stand: 2026-05-07 · Aktuelle Version: 1.0.1

---

## ✅ Phase 1+2 – Ordnungsprojekte

- Modelle `Project` + `Step` in `models.py`
- CRUD in `storage.py` (eigene TinyDB-Tabellen `projects`, `project_steps`)
- Routen `/projects`, `/projects/new`, `/projects/{id}`, Steps abhaken/löschen
- Punkte pro Step, getrennte Statistik (Haushaltsaufgaben vs. Projektschritte)

---

## ✅ Phase 3+4 – Design + Dashboard

- Warm-Rose/Mauve Farbschema mit CSS-Variablen (`--primary: #b5738a`)
- Bottom-Navigation (5 Tabs: Zuhause / Aufgaben / Projekte / Punkte / Einstellungen)
- Dashboard als neue Startseite `/`: Begrüßung, Statistik-Kacheln, Raumkarten-Grid
- Aufgabenliste auf `/tasks` verschoben

---

## ✅ Refactoring – Modulstruktur

- `main.py` auf ~35 Zeilen schlankt
- `config.py`: ADMINS, Logger
- `render.py`: HTML/CSS-Template, Hilfsfunktionen
- `scheduler.py`: Benachrichtigungslogik
- `routes/`: dashboard, tasks, projects, scores, settings (je eigene Datei)

---

## ✅ Logo & Assets

- SVG-Logo (Haus + Häkchen im Rose/Mauve-Gradient)
- PNG-Icon für HA Add-on Store (`icon.png`, 256×256)
- Logo als Favicon und Header-Icon in der Web-UI
- Assets werden via FastAPI StaticFiles unter `/assets/` ausgeliefert

---

## Phase 5 – Komfort-Features

Ziel: Nützliche Erweiterungen für den Alltag.

- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications
- **Einmalige Aufgaben**: `task_type = onetime`, nach Erledigung archiviert
- **Wichtig-Flag**: hervorgehoben in der Aufgabenliste
- **Aufwand-Feld**: gering / mittel / hoch als Chip
- **Leaderboard-Tabs**: Monat / Letzter Monat / Gesamt
- **Projekte auto-archivieren**: wenn alle Schritte erledigt
- **Benachrichtigungen für Projekte**: offene Schritte in Daily-Push erwähnen
- **Räume pro Person ausblenden**: individuelle Raumauswahl in den Einstellungen

---

## Phase 6 – Gamification & Statistik

Ziel: Motivation langfristig erhalten.

- **Wochenziele**: pro Person konfigurierbar (z.B. 5 Aufgaben / Woche)
- **Achievements / Abzeichen**: erste Aufgabe, 10er-Serie, Monatsbester …
- **Persönliche Statistik-Seite**: Verlauf, Streak, Lieblingsraum
- **Dark Mode / Light Mode**: umschaltbar, folgt optional dem HA-Theme

---

## Phase 7 – Familie & Kommunikation

Ziel: Gemeinsames Arbeiten erleichtern.

- **Kommentare**: Notizen zu Aufgaben und Projekten hinterlassen
- **Erinnerung senden**: andere Person auf offene Aufgabe hinweisen ("Küche ist noch offen")
- **Einkaufsliste**: eigener Bereich, ähnlich wie Projekte, ohne Intervall

---

## Phase 8 – Foto-Dokumentation

Ziel: Visuelle Hinweise und Vorher/Nachher-Dokumentation.

- Fotos pro Aufgabe: Hinweisfoto (wo/was) + Vorher/Nachher bei Erledigung
- Fotos pro Projekt und Schritt: Fortschrittsdokumentation
- Upload via FastAPI (`UploadFile`), Ablage unter `/data/photos/`
- Anzeige als Thumbnail in Aufgaben- und Projektansicht

---

## Phase 9 – Integrationen & Erweiterungen

Ziel: Tiefer in das HA-Ökosystem einbinden.

- **HA-Sensoren/Entities**: Aufgabenstatus als HA-Entity (für Automationen)
- **Trash Card**: Müllkalender-Termine als Aufgaben-Trigger
- **REST-API**: Aufgaben per HA-Automation anlegen
- **Aufgaben-Vorlagen**: häufige Sets speichern (z.B. "Frühjahrsputz")
- **Tags / Kategorien**: zusätzlich zu Räumen
- **Mehrsprachigkeit**: Deutsch / Englisch
- **Daten-Export**: CSV / JSON-Backup der gesamten Datenbank

---

## Bereits umgesetzt (v1.0.1)

- Aufgaben-CRUD (anlegen, bearbeiten, löschen, abhaken)
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- Ordnungsprojekte mit Teilschritten und Fortschrittsbalken
- HA-Räume und Personen per Template-API
- Punkte und Bestenliste (getrennt: Aufgaben vs. Projektschritte)
- Per-Person Push-Benachrichtigungen mit eigenem Zeitplan
- Admin-Rollentrennung (Geräte vs. persönliche Einstellungen)
- HA Ingress-Navigation
- Rose/Mauve Design-System, Bottom-Navigation, Dashboard
- Modulare Codebasis (`routes/`, `render`, `scheduler`, `config`)
- SVG-Logo + PNG-Icon, Favicon in der Web-UI
