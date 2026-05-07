# TidyHome – Roadmap

Stand: 2026-05-07 · Aktuelle Version: 1.0.9

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

- `main.py` auf ~35 Zeilen schlank
- `config.py`: Logger, Bootstrap-Admins
- `render.py`: HTML/CSS-Template, Hilfsfunktionen, `resolve_person()`
- `scheduler.py`: Benachrichtigungslogik
- `routes/`: dashboard, tasks, projects, scores, settings (je eigene Datei)

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

## ✅ Phase 6 – Weitere Komfort-Features (v1.0.5)

- **Einmalige Aufgaben**: nach Erledigung automatisch archiviert, `1×`-Badge in der Liste
- **Räume pro Person ausblenden**: Checkboxen in den Einstellungen, wirkt auf Dashboard, Aufgaben und Projekte
- **Projekt-Benachrichtigungen**: offene Projektschritte in der täglichen Push-Benachrichtigung
- **Einstellungen aufgeteilt**: persönliche Einstellungen auf `/settings`, alle Personen im Admin-Panel

---

## ✅ Phase 7 – Gamification & Statistik (v1.0.6)

- **Dark Mode**: folgt automatisch dem System-/HA-Theme via `prefers-color-scheme`
- **Persönliche Statistik**: Streak, Punkte diese Woche, Gesamt-Punkte auf der Punkte-Seite
- **Wochenziel**: pro Person konfigurierbar, Fortschrittsbalken auf der Punkte-Seite
- **Leaderboard-Highlight**: eigene Zeile farblich hervorgehoben

---

## ✅ Phase 8 – Authentifizierung & Rollen (v1.0.7–1.0.9)

- **HA-Login-Erkennung**: Person wird automatisch via `X-Remote-User-Display-Name` erkannt
- **Admin-Personenwechsel**: Admins können per `▾`-Pill die Ansicht wechseln
- **Rollen-System**: Elternteil / Kind / Haushaltshilfe / Mitglied im Admin-Panel vergeben
- **Rollenbasierte Sichtbarkeit**: Elternteil/Admin sieht alle Aufgaben; Kind optional andere Kinder; Mitglied/Haushaltshilfe nur eigene
- **Raum-Gruppenansicht**: Elternteil/Admin sieht Aufgaben im Raum-Filter nach Person gruppiert
- **Aufgaben-Default**: neue Aufgaben werden automatisch dem angemeldeten Nutzer zugeordnet

---

## Phase 9 – Familie & Kommunikation

Ziel: Gemeinsames Arbeiten erleichtern.

- **Kommentare**: Notizen zu Aufgaben und Projekten hinterlassen
- **Erinnerung senden**: andere Person auf offene Aufgabe hinweisen
- **Einkaufsliste**: eigener Bereich ohne Intervall
- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications

---

## Phase 10 – Barrierefreiheit & Neurodiversität

Ziel: Die App für Menschen mit ADHS, Depressionen, Autismus u.a. zugänglich machen.

- **Fokus-Modus**: reduzierte Ansicht mit nur 1–3 Aufgaben pro Tag
- **Sanfte Sprache**: "noch offen" statt "überfällig"
- **Energielevel-Modus**: Aufgaben nach Aufwand filtern je nach Tagesverfassung
- **Aufgaben-Pausen**: Intervalle temporär einfrieren
- **Positive Verstärkung**: ermutigende Meldungen bei Erledigung
- **Strukturhilfe**: Aufgaben in kleine Teilschritte aufteilen

---

## Phase 11 – Haushaltshilfe-Verwaltung

Ziel: Bezahlte Haushaltshilfen verwalten, Zeiten erfassen und Kosten tracken.

- **Zeiterfassung**: Arbeitsbeginn/-ende stempeln oder manuell eintragen
- **Stundensatz**: durch Admin hinterlegt, für die Haushaltshilfe nicht sichtbar
- **Kostenübersicht**: Stunden × Stundensatz, filterbar nach Monat / Zeitraum
- **CSV-Export**: für Abrechnung oder Steuererklärung

---

## Phase 12 – Foto-Dokumentation

Ziel: Visuelle Hinweise und Vorher/Nachher-Dokumentation.

- Fotos pro Aufgabe: Hinweisfoto (wo/was) + Vorher/Nachher bei Erledigung
- Fotos pro Projekt und Schritt: Fortschrittsdokumentation
- Upload via FastAPI (`UploadFile`), Ablage unter `/data/photos/`
- Anzeige als Thumbnail in Aufgaben- und Projektansicht

---

## Phase 13 – Integrationen & Erweiterungen

Ziel: Tiefer in das HA-Ökosystem einbinden und die App abrunden.

- **HA-Sensoren/Entities**: Aufgabenstatus als HA-Entity (für Automationen)
- **Trash Card**: Müllkalender-Termine als Aufgaben-Trigger
- **REST-API**: Aufgaben per HA-Automation anlegen
- **Aufgaben-Vorlagen**: häufige Sets speichern (z.B. "Frühjahrsputz")
- **Tags / Kategorien**: zusätzlich zu Räumen
- **Mehrsprachigkeit**: Deutsch / Englisch
- **Daten-Export**: CSV / JSON-Backup der gesamten Datenbank

---

## Bereits umgesetzt (v1.0.9)

- Aufgaben-CRUD (anlegen, bearbeiten, löschen, abhaken)
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- Einmalige Aufgaben (nach Erledigung archiviert)
- Wichtig-Flag: Stern-Badge, orange Markierung, Sortierung oben
- Ordnungsprojekte mit Teilschritten und Fortschrittsbalken
- Projekte auto-abschließen wenn alle Schritte erledigt; Abgeschlossen-Tab
- HA-Räume und Personen per Template-API
- Punkte und Bestenliste (Gesamt / Dieser Monat / Letzter Monat)
- Persönliche Statistik: Streak, Wochenpunkte, Wochenziel mit Fortschrittsbalken
- Per-Person Push-Benachrichtigungen (Aufgaben + Projektschritte) mit eigenem Zeitplan
- Admin-Verwaltung per Checkbox; Geräte-Verwaltung per Checkbox
- Rollen-System: Elternteil / Kind / Haushaltshilfe / Mitglied
- Rollenbasierte Sichtbarkeit und Raum-Gruppenansicht für Elternteil/Admin
- Person automatisch aus HA-Login erkannt; Admins können Ansicht wechseln
- Räume pro Person individuell ausblendbar
- Dark Mode (folgt System-/HA-Theme automatisch)
- HA Ingress-Navigation, `p`-Parameter bleibt beim Navigieren erhalten
- Rose/Mauve Design-System, Bottom-Navigation, Dashboard
- Modulare Codebasis (`routes/`, `render`, `scheduler`, `config`)
- SVG-Logo + PNG-Icon, Favicon; CHANGELOG.md für HA Update-Dialog
