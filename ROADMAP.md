# TidyHome – Roadmap

Stand: 2026-05-07 · Aktuelle Version: 1.0.4

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

## ✅ Phase 5 – Komfort-Features (v1.0.2–1.0.4)

- **Logo & Assets**: SVG-Logo, PNG-Icon für HA Add-on Store, Favicon in der Web-UI
- **Admin-Verwaltung per Checkbox**: Personen aus HA als Admin markierbar (kein Freitext mehr)
- **Geräte-Verwaltung per Checkbox**: Notify-Services automatisch aus HA geladen
- **Wichtig-Flag**: Stern-Badge + orange Markierung, wichtige Aufgaben oben sortiert
- **Projekte auto-archivieren**: automatisch abschließen wenn alle Schritte erledigt; eigener "Abgeschlossen"-Tab
- **Leaderboard-Tabs**: Gesamt / Dieser Monat / Letzter Monat (via `score_log`-Tabelle)
- **CHANGELOG.md**: Versionshistorie für HA Update-Dialog

---

## Phase 6 – Weitere Komfort-Features

Ziel: Nützliche Erweiterungen für den Alltag.

- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications
- **Einmalige Aufgaben**: `task_type = onetime`, nach Erledigung archiviert
- **Aufwand-Feld**: gering / mittel / hoch als Chip
- **Benachrichtigungen für Projekte**: offene Schritte in Daily-Push erwähnen
- **Räume pro Person ausblenden**: individuelle Raumauswahl in den Einstellungen

---

## Phase 7 – Gamification & Statistik

Ziel: Motivation langfristig erhalten.

- **Wochenziele**: pro Person konfigurierbar (z.B. 5 Aufgaben / Woche)
- **Achievements / Abzeichen**: erste Aufgabe, 10er-Serie, Monatsbester …
- **Persönliche Statistik-Seite**: Verlauf, Streak, Lieblingsraum
- **Dark Mode / Light Mode**: umschaltbar, folgt optional dem HA-Theme

---

## Phase 8 – Familie & Kommunikation

Ziel: Gemeinsames Arbeiten erleichtern.

- **Kommentare**: Notizen zu Aufgaben und Projekten hinterlassen
- **Erinnerung senden**: andere Person auf offene Aufgabe hinweisen ("Küche ist noch offen")
- **Einkaufsliste**: eigener Bereich, ähnlich wie Projekte, ohne Intervall

---

## Phase 9 – Barrierefreiheit & Neurodiversität

Ziel: Die App für Menschen mit ADHS, Depressionen, Autismus u.a. zugänglich machen.

- **Fokus-Modus**: reduzierte Ansicht mit nur 1–3 Aufgaben pro Tag (weniger Reizüberflutung)
- **Sanfte Sprache**: "noch offen" statt "überfällig", keine negativen Formulierungen
- **Energielevel-Modus**: Aufgaben nach Aufwand filtern je nach Tagesverfassung
- **Aufgaben-Pausen**: Intervalle gezielt einfrieren (z.B. bei depressiven Episoden)
- **Positive Verstärkung**: ermutigende Meldungen bei Erledigung, keine Straf-Mechanismen
- **Erinnerungsabstand**: sanftere Benachrichtigungsfrequenz pro Person einstellbar
- **Strukturhilfe**: Aufgaben automatisch in kleine Teilschritte vorschlagen

---

## Phase 10 – Haushaltshilfe-Verwaltung

Ziel: Bezahlte Haushaltshilfen verwalten, Zeiten erfassen und Kosten tracken.

- **Rolle "Haushaltshilfe"**: eigene Kennzeichnung, durch Admin verwaltbar
- **Zeiterfassung**: Arbeitsbeginn/-ende stempeln oder manuell eintragen
- **Stundensatz**: durch Admin hinterlegt, für die Haushaltshilfe nicht sichtbar
- **Kostenübersicht**: Stunden × Stundensatz, filterbar nach Monat / Zeitraum
- **Aufgaben-Protokoll**: welche Aufgaben wurden in welchem Einsatz erledigt
- **CSV-Export**: für Abrechnung oder Steuererklärung (haushaltsnahe Dienstleistungen)

---

## Phase 11 – Foto-Dokumentation

Ziel: Visuelle Hinweise und Vorher/Nachher-Dokumentation.

- Fotos pro Aufgabe: Hinweisfoto (wo/was) + Vorher/Nachher bei Erledigung
- Fotos pro Projekt und Schritt: Fortschrittsdokumentation
- Upload via FastAPI (`UploadFile`), Ablage unter `/data/photos/`
- Anzeige als Thumbnail in Aufgaben- und Projektansicht

---

## Phase 12 – Integrationen & Erweiterungen

Ziel: Tiefer in das HA-Ökosystem einbinden und die App abrunden.

- **HA-Sensoren/Entities**: Aufgabenstatus als HA-Entity (für Automationen)
- **Trash Card**: Müllkalender-Termine als Aufgaben-Trigger
- **REST-API**: Aufgaben per HA-Automation anlegen
- **Aufgaben-Vorlagen**: häufige Sets speichern (z.B. "Frühjahrsputz")
- **Tags / Kategorien**: zusätzlich zu Räumen
- **Mehrsprachigkeit**: Deutsch / Englisch
- **Daten-Export**: CSV / JSON-Backup der gesamten Datenbank

---

## Bereits umgesetzt (v1.0.4)

- Aufgaben-CRUD (anlegen, bearbeiten, löschen, abhaken)
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- Wichtig-Flag: Stern-Badge, orange Markierung, Sortierung oben
- Ordnungsprojekte mit Teilschritten und Fortschrittsbalken
- Projekte auto-abschließen wenn alle Schritte erledigt; Archivieren-Tab
- HA-Räume und Personen per Template-API
- Punkte und Bestenliste (Gesamt / Dieser Monat / Letzter Monat)
- Getrennte Statistik: Haushaltsaufgaben vs. Projektschritte
- Per-Person Push-Benachrichtigungen mit eigenem Zeitplan
- Admin-Verwaltung per Checkbox (Personen aus HA)
- Geräte-Verwaltung per Checkbox (Notify-Services aus HA)
- HA Ingress-Navigation
- Rose/Mauve Design-System, Bottom-Navigation, Dashboard
- Modulare Codebasis (`routes/`, `render`, `scheduler`, `config`)
- SVG-Logo + PNG-Icon, Favicon in der Web-UI
- CHANGELOG.md für HA Update-Dialog
