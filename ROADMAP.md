# TidyHome – Roadmap

Stand: 2026-05-08 · Aktuelle Version: 1.3.5

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

- Logo & Assets: SVG-Logo, PNG-Icon für HA Add-on Store, Favicon
- Admin-Verwaltung per Checkbox: Personen aus HA als Admin markierbar
- Geräte-Verwaltung per Checkbox: Notify-Services automatisch aus HA geladen
- Wichtig-Flag: Stern-Badge + orange Markierung, wichtige Aufgaben oben sortiert
- Projekte auto-archivieren: automatisch abschließen wenn alle Schritte erledigt
- Leaderboard-Tabs: Gesamt / Dieser Monat / Letzter Monat
- CHANGELOG.md: Versionshistorie für HA Update-Dialog

---

## ✅ Phase 6 – Weitere Komfort-Features (v1.0.5)

- Einmalige Aufgaben: nach Erledigung automatisch archiviert, `1×`-Badge
- Räume pro Person ausblenden: Checkboxen in den Einstellungen
- Projekt-Benachrichtigungen: offene Projektschritte in der täglichen Push-Benachrichtigung
- Einstellungen aufgeteilt: persönliche Einstellungen auf `/settings`, alle Personen im Admin-Panel

---

## ✅ Phase 7 – Gamification & Statistik (v1.0.6)

- Dark Mode: folgt automatisch dem System-/HA-Theme
- Persönliche Statistik: Streak, Punkte diese Woche, Gesamt-Punkte
- Wochenziel: pro Person konfigurierbar, Fortschrittsbalken
- Leaderboard-Highlight: eigene Zeile farblich hervorgehoben

---

## ✅ Phase 8 – Authentifizierung & Rollen (v1.0.7–1.0.9)

- HA-Login-Erkennung: Person via `X-Remote-User-Display-Name`
- Admin-Personenwechsel: Admins können per `▾`-Pill die Ansicht wechseln
- Rollen-System: Elternteil / Kind / Haushaltshilfe / Mitglied
- Rollenbasierte Sichtbarkeit und Raum-Gruppenansicht
- Aufgaben-Default: neue Aufgaben werden automatisch dem angemeldeten Nutzer zugeordnet

---

## ✅ Phase 9 – Modern UI Refresh (v1.1.0–1.2.10)

- Design-System aufgefrischt: neutrale Flächen, Mauve/Rose nur als Akzent
- Light/Dark Tokens: gemeinsame CSS-Variablen; externes Stylesheet `assets/app.css`
- FOUC-Fix: inline Critical CSS + body opacity verhindert Aufblitzen
- Dashboard als Heute-Ansicht: Ring-Charts, nächste Aufgaben, Räume als Liste
- Dashboard: Schnellaktions-Buttons "+ Aufgabe" und "+ Projekt"
- Dashboard: Räume nur mit eigenen Aufgaben/Projekten; fremde Räume für Admins/Eltern abgesetzt
- Aufgaben kompaktes Layout: Aktionsbuttons rechts inline, kein separater Aktionsblock
- Neue `--sep`-Variable für garantiert sichtbare Listentrennlinien in Light/Dark Mode
- Raum-Icons: visueller Klick-Picker im Admin-Bereich
- Admin-Panel: HTML-Bugs behoben, klare Abschnittsgliederung
- OpenMoji Icons: 44 farbige Illustrationen, Icon-Chooser in Formularen
- SVG-Aktions-Buttons, Empty States, Filter-Chip-Leiste

---

## ✅ Phase 11 – Aufgaben-Komfort (v1.3.x)

- **Aufwand-Feld**: wenig / mittel / viel — Badge in der Zeile, Filter-Chip in der Liste
- **Startdatum**: Aufgabe erst ab einem bestimmten Datum sichtbar und fällig
- **Fälligkeit einmalig verschieben (Snooze)**: Schnell-Seite mit +1/+3/+7/+14/+30 Tage und eigenem Datum; Snooze-Button direkt in der Aufgabenzeile; Verschiebung wird nach Erledigung automatisch aufgehoben
- **Erweiterte OpenMoji-Icons**: größere Raum-/Orts-Auswahl im Admin-Bereich, konservative automatische Raumerkennung per Teilstring
- **Projekt-Icons**: Projektformulare bieten Aufgaben-Icons und Raum-/Orts-Icons gemeinsam an

---

## Phase 10 – Familie & Kommunikation

Ziel: Gemeinsames Arbeiten erleichtern.

- **Kommentare**: Notizen zu Aufgaben und Projekten hinterlassen
- **Erinnerung senden**: andere Person auf offene Aufgabe hinweisen
- **Einkaufsliste**: eigener Bereich ohne Intervall, gemeinsam bearbeitbar
- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications

---

## Phase 12 – Barrierefreiheit & Neurodiversität

Ziel: Die App für Menschen mit ADHS, Depressionen, Autismus u.a. zugänglich machen.

- **Fokus-Modus**: reduzierte Ansicht mit nur 1–3 Aufgaben pro Tag
- **Sanfte Sprache**: "noch offen" statt "überfällig"
- **Energielevel-Modus**: Aufgaben nach Aufwand filtern je nach Tagesverfassung
- **Positive Verstärkung**: ermutigende Meldungen bei Erledigung

---

## Phase 13 – Haushaltshilfe-Verwaltung

Ziel: Bezahlte Haushaltshilfen verwalten, Zeiten erfassen und Kosten tracken.

- **Zeiterfassung**: Arbeitsbeginn/-ende stempeln oder manuell eintragen
- **Stundensatz**: durch Admin hinterlegt, für die Haushaltshilfe nicht sichtbar
- **Kostenübersicht**: Stunden × Stundensatz, filterbar nach Monat / Zeitraum
- **CSV-Export**: für Abrechnung oder Steuererklärung

---

## Phase 14 – Foto-Dokumentation

Ziel: Visuelle Hinweise und Vorher/Nachher-Dokumentation.

- Fotos pro Aufgabe: Hinweisfoto (wo/was) + Vorher/Nachher bei Erledigung
- Fotos pro Projekt und Schritt: Fortschrittsdokumentation
- Upload via FastAPI (`UploadFile`), Ablage unter `/data/photos/`
- Anzeige als Thumbnail in Aufgaben- und Projektansicht

---

## Phase 15 – HA-Integration & Erweiterungen

Ziel: Tiefer in das HA-Ökosystem einbinden.

- **HA-Sensoren/Entities**: Aufgabenstatus als HA-Entity (für Automationen)
- **REST-API**: Aufgaben per HA-Automation anlegen
- **Aufgaben-Vorlagen**: häufige Sets speichern (z.B. "Frühjahrsputz")
- **Tags / Kategorien**: zusätzlich zu Räumen
- **Trash Card**: Müllkalender-Termine als Aufgaben-Trigger
- **Mehrsprachigkeit**: Deutsch / Englisch
- **Daten-Export**: CSV / JSON-Backup der gesamten Datenbank
