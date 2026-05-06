# TidyHome – Roadmap

Stand: 2026-05-06. Phasen sind sequenziell geplant; jede Phase wird als eigener Commit abgeschlossen.

---

## Phase 1+2 – Ordnungsprojekte (Datenmodell + UI)

Ziel: Aufgaben mit Teilschritten ("Ordnungsprojekte") verwalten.

- `models.py`: neues Modell `Project` (id, name, room, assigned_to, created_at) + `Step` (id, project_id, name, completed, points)
- `storage.py`: CRUD fuer Projects + Steps (eigene TinyDB-Tabellen)
- `main.py`: Routen `/projects`, `/projects/new`, `/projects/{id}`, POST Step abhaken
- Punkte werden pro Step gutgeschrieben (wie bei Tasks)
- Projekte sind einmalig (kein Intervall); archiviert wenn alle Steps erledigt
- Statistik trennt Haushaltsaufgaben vs. Projektaufgaben

Worauf achten:
- Bestehende Tasks mit Defaults absichern (keine Migration noetig)
- Steps in separater Tabelle `project_steps`

---

## Phase 3+4 – Design + Dashboard

Ziel: Betidy-inspiriertes Design und personalisierte Startseite.

Design-System:
- Farbschema: Warm-Rose/Mauve (`#c084a0`) statt Blau
- Karten-Layout, mehr Weissraum, groessere Touch-Targets
- Bottom-Navigation (position: fixed): Zuhause / Aufgaben / Projekte / Punkte / Einstellungen
- Content-Bereich bekommt `padding-bottom` fuer Bottom-Nav

Dashboard (neue Startseite `/`):
- "Hallo [Person]"-Begruessung (Person per `?person=Name` oder Cookie)
- Kacheln: Tagesaufgaben (erledigt/gesamt), Ueberfaellig, Aufgaben & Projekte gesamt
- Gesamtzustand-Fortschrittsbalken (erledigte Tasks letzte 30 Tage)
- Raumkarten-Grid: offene Aufgaben + Projekte + Mini-Fortschrittsbalken pro Raum

Aufgabenliste zieht auf `/tasks` um (war `/`).

Worauf achten:
- HA Ingress: kein echtes Vollbild-Mobile, Bottom-Nav muss mit Ingress-Hoehe umgehen
- Raumkarten ohne Fotos: Farbflächen mit Emoji/Icon

---

## Phase 5 – Zusatz-Features

Ziel: Komfort-Features aus Betidy.

- **Urlaubsmodus**: globaler Toggle in Settings → Intervall-Berechnung eingefroren
- **Einmalige Aufgaben**: `task_type = onetime`, nach Erledigung archiviert
- **Wichtig-Flag**: hervorgehoben in der Liste
- **Aufwand-Feld**: gering / mittel / hoch als Chip
- **Leaderboard-Tabs**: Monat / Letzter Monat / Gesamt (Punkte nach Zeitraum)

---

## Bereits umgesetzt (v0.8.0)

- Aufgaben-CRUD mit Bearbeiten
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- HA-Raeume und Personen per Template-API
- Punkte und Bestenliste
- Per-Person Benachrichtigungen mit eigenem Zeitplan
- Admin-Rollentrennung (Geraete vs. persoenliche Einstellungen)
- HA Ingress-Navigation
