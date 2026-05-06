# TidyHome – Roadmap

Stand: 2026-05-06. Phasen sind sequenziell geplant; jede Phase wird als eigener Commit abgeschlossen.

---

## ✅ Phase 1+2 – Ordnungsprojekte (abgeschlossen)

- Modelle `Project` + `Step` in `models.py`
- CRUD in `storage.py` (eigene TinyDB-Tabellen)
- Routen `/projects`, `/projects/new`, `/projects/{id}`, Steps abhaken/loeschen
- Punkte pro Step, getrennte Statistik (Haushaltsaufgaben vs. Projektschritte)

---

## ✅ Phase 3+4 – Design + Dashboard (abgeschlossen)

- Warm-Rose/Mauve Farbschema mit CSS-Variablen
- Bottom-Navigation (5 Tabs: Zuhause / Aufgaben / Projekte / Punkte / Einstellungen)
- Dashboard als neue Startseite `/`: Begruessung, Statistik-Kacheln, Raumkarten-Grid
- Aufgabenliste auf `/tasks` verschoben

---

## ✅ Refactoring – Modulstruktur (abgeschlossen)

- `main.py` auf ~35 Zeilen schlankt
- `config.py`: ADMINS, Logger
- `render.py`: HTML/CSS-Template, Hilfsfunktionen
- `scheduler.py`: Benachrichtigungslogik
- `routes/`: dashboard, tasks, projects, scores, settings (je eigene Datei)

---

## Phase 5 – Zusatz-Features

Ziel: Komfort-Features und Erweiterungen.

- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications
- **Einmalige Aufgaben**: `task_type = onetime`, nach Erledigung archiviert
- **Wichtig-Flag**: hervorgehoben in der Aufgabenliste
- **Aufwand-Feld**: gering / mittel / hoch als Chip
- **Leaderboard-Tabs**: Monat / Letzter Monat / Gesamt
- **Projekte auto-archivieren**: wenn alle Schritte erledigt

---

## Phase 6 – Foto-Dokumentation

Ziel: Visuelle Hinweise und Vorher/Nachher-Dokumentation.

- Fotos pro Aufgabe: Hinweisfoto (wo/was) + Vorher/Nachher bei Erledigung
- Fotos pro Projekt und Schritt: Fortschrittsdokumentation
- Upload via FastAPI (`UploadFile`), Ablage unter `/data/photos/`
- Anzeige als Thumbnail in Aufgaben- und Projektansicht

---

## Phase 7 – Integrationen

Ziel: Tiefer in das HA-Oekosystem einbinden.

- **HA-Sensoren/Entities**: Aufgabenstatus als HA-Entity (fuer Automationen)
- **Trash Card**: Muellkalender-Termine als Aufgaben-Trigger
- **Benachrichtigungen fuer Projekte**: offene Schritte in Daily-Push erwaehnen

---

## Bereits umgesetzt (v1.0.0)

- Aufgaben-CRUD (anlegen, bearbeiten, loeschen, abhaken)
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- Ordnungsprojekte mit Teilschritten und Fortschrittsbalken
- HA-Raeume und Personen per Template-API
- Punkte und Bestenliste (getrennt: Aufgaben vs. Projektschritte)
- Per-Person Push-Benachrichtigungen mit eigenem Zeitplan
- Admin-Rollentrennung (Geraete vs. persoenliche Einstellungen)
- HA Ingress-Navigation
- Rose/Mauve Design-System, Bottom-Navigation, Dashboard
- Modulare Codebasis (routes/, render, scheduler, config)
