# TidyHome – Roadmap

Stand: 2026-05-07 · Aktuelle Version: 1.1.5

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
- **Admin-Verwaltung per Checkbox**: Personen aus HA als Admin markierbar
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

## ✅ Phase 9 – Modern UI Refresh (v1.1.0–1.1.4)

- **Design-System aufgefrischt**: neutrale Flächen, Mauve/Rose nur als Akzent, klare Statusfarben
- **Light/Dark Tokens**: gemeinsame CSS-Variablen; externes Stylesheet `assets/app.css`
- **FOUC-Fix**: inline Critical CSS + `color-scheme` Meta verhindert Aufblitzen beim Seitenswitch
- **Dashboard als Heute-Ansicht**: Ring-Charts (Erledigt/Überfällig/Zustand) als einzelne Karten, nächste Aufgaben, Räume als Liste
- **Aufgaben 3-Zeilen-Layout**: Name+Badge / Datum / Aktionen — klare Dichte auf Mobile
- **Badge-Semantik**: "Geplant" / "Heute" / "Überfällig" als Status; Timing separat ("Morgen", "In 3 Tagen")
- **Kategorie-Icons**: Aufgaben bekommen thematische SVG-Icons nach Name/Raum
- **"Meine"-Filter**: zeigt nur dem aktiven Nutzer zugeordnete Aufgaben
- **Projekte als Cards**: Fortschrittsbalken, nächster Schritt, Icon-Aktionen
- **Formulare**: SVG-Stern statt Emoji, Personen full-width, verbesserter Back-Button
- **SVG-Aktions-Buttons**: Erledigt/Bearbeiten/Löschen als konsistente Icon-Buttons
- **Empty States**: illustrierte Meldungen bei leerer Aufgaben-/Projektliste
- **OpenMoji Icons**: 44 farbige Illustrationen für Haushalt und Familie, vollständig offline
- **Icon-Chooser**: manuelle Icon-Auswahl im Formular, überschreibt die automatische Erkennung
- **Keyword-Erkennung**: Haustiere, Kinder, Auto, Reparatur, Garten, Küche und mehr
- **Bugfix**: Projekt-URLs absolut — Schritte hinzufügen/abhaken/löschen und Navigation repariert

---

## Phase 10 – Familie & Kommunikation

Ziel: Gemeinsames Arbeiten erleichtern.

- **Kommentare**: Notizen zu Aufgaben und Projekten hinterlassen
- **Erinnerung senden**: andere Person auf offene Aufgabe hinweisen ("Küche ist noch offen")
- **Einkaufsliste**: eigener Bereich ohne Intervall, gemeinsam bearbeitbar
- **Urlaubsmodus**: globaler Toggle → Intervall-Berechnung eingefroren, keine Notifications

---

## Phase 11 – Aufgaben-Komfort

Ziel: Flexiblere Aufgabensteuerung ohne Overhead.

- **Startdatum wählbar**: Aufgabe beginnt erst ab einem bestimmten Datum zu laufen
- **Aufwand-Feld**: gering / mittel / hoch, als zusätzlicher Filter
- **Fälligkeit manuell verschieben**: einmalige Ausnahme ohne Intervall zu ändern
- **Aufgaben-Pausen**: Intervalle temporär einfrieren (z.B. Urlaub, Krankheit)
- **Kalenderstreifen**: Wochenübersicht mit Aufgaben pro Tag

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

---

## Bereits umgesetzt (v1.1.2)

- Aufgaben-CRUD (anlegen, bearbeiten, löschen, abhaken)
- Wiederkehrende Intervalle (1/2/7/14/30/90/180/365 Tage)
- Einmalige Aufgaben (nach Erledigung archiviert)
- Wichtig-Flag: Stern-Badge, orange Markierung, Sortierung oben
- Aufgaben können mehreren Personen gleichzeitig zugeordnet werden
- 3-Zeilen-Layout: Name+Badge / Datum / Aktionen; Badge-Semantik Geplant/Heute/Überfällig
- "Meine"-Filter: zeigt nur eigene Aufgaben
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
- Dark Mode (folgt System-/HA-Theme automatisch), FOUC-Fix
- HA Ingress-Navigation, `p`-Parameter bleibt beim Navigieren erhalten
- Design-System: Mauve/Rose-Tokens, Light/Dark, externes Stylesheet `assets/app.css`
- Dashboard: Ring-Charts als einzelne Karten, nächste Aufgaben, Räume als Liste
- Kategorie-Icons für Aufgaben; SVG-Aktions-Buttons; Empty States
- Formulare: SVG-Icons, full-width Personenzuweisung, konsistenter Back-Button
- OpenMoji Icons (44 SVGs offline): farbige Aufgaben- und Projekt-Bubbles nach Kategorie
- Icon-Chooser in Aufgaben- und Projekt-Formularen mit 🔮 Auto-Option
- Aktionen in Aufgaben über volle Breite: Haken links, Edit/Löschen rechts
- Bugfix: Projekt-Detailansicht (Schritte, Navigation) mit absoluten URLs
- Modulare Codebasis (`routes/`, `render`, `scheduler`, `config`)
- SVG-Logo + PNG-Icon, Favicon; CHANGELOG.md für HA Update-Dialog
