# TidyHome - Features

Stand: 2026-05-08 · Version 1.3.16

Status: `[x]` umgesetzt · `[ ]` geplant · `[idee]` Idee

---

## Kernfunktionen

### Aufgaben

- [x] Aufgaben anlegen, bearbeiten, löschen und erledigen
- [x] Wiederkehrende Intervalle von täglich bis jährlich
- [x] Einmalige Aufgaben mit automatischer Archivierung nach Erledigung
- [x] Startdatum: Aufgaben erst ab einem gewählten Datum sichtbar und fällig
- [x] Fälligkeit einmalig verschieben, ohne das Intervall zu ändern
- [x] Statusanzeige für geplant, heute, überfällig und ok
- [x] Raum, Punkte, Aufwand und Wichtig-Flag pro Aufgabe
- [x] Mehrfachzuweisung an mehrere Personen
- [x] Neue Aufgaben werden standardmäßig der angemeldeten Person zugeordnet
- [x] Filter nach Raum, Person, Überfälligkeit und Aufwand
- [x] Kommentare und Notizen direkt an Aufgaben
- [x] Erinnerung an andere zugewiesene Personen senden

### Projekte

- [x] Projekte mit Name, Raum, Person, Beschreibung und Icon
- [x] Projektschritte hinzufügen, erledigen und löschen
- [x] Punkte pro Projektschritt
- [x] Fortschrittsbalken pro Projekt
- [x] Automatischer Projektabschluss, wenn alle Schritte erledigt sind
- [x] Abgeschlossene Projekte in eigener Ansicht mit Archivierung
- [x] Kommentare und Notizen direkt an Projekten
- [x] Erinnerung an zuständige Person eines offenen Projektschritts senden
- [x] Projektliste zeigt offene Schritte bei anderen Personen direkt an
- [x] Projekt-Icons aus Aufgaben-, Raum- und Orts-Icons auswählbar

### Zuhause & Navigation

- [x] Dashboard als persönliche Heute-Ansicht
- [x] Tagesstatistik, nächste Aufgaben und Raumübersicht
- [x] Schnellaktionen für neue Aufgaben und Projekte
- [x] Bottom-Navigation für Zuhause, Aufgaben, Projekte, Punkte und Einstellungen
- [x] Bottom-Navigation mit lokalen OpenMoji-Icons
- [x] Person bleibt beim Navigieren erhalten
- [x] Admins können zwischen Personenansichten wechseln
- [x] Überarbeitetes Personenmenü mit klaren Bereichen für Ansicht, Einstellungen und Verwaltung

### Punkte & Motivation

- [x] Punkte für erledigte Aufgaben
- [x] Punkte für erledigte Projektschritte
- [x] Bestenliste für Gesamt, aktuellen Monat und letzten Monat
- [x] Eigene Zeile im Leaderboard hervorgehoben
- [x] Getrennte Auswertung für Haushaltsaufgaben und Projektschritte
- [x] Persönliche Statistik mit Streak, Wochenpunkten, Gesamtpunkten und Wochenziel

### Benachrichtigungen & Erinnerungen

- [x] Tägliche Push-Benachrichtigung mit fälligen Aufgaben
- [x] Offene Projektschritte in der täglichen Benachrichtigung
- [x] Eigene Uhrzeit und Geräte pro Person
- [x] Notify-Services aus Home Assistant auswählbar
- [x] Test-Benachrichtigung direkt aus der UI
- [x] Reminder-Glocke nur, wenn andere Empfänger vorhanden sind
- [x] Reminder für Aufgaben mit mehreren Empfängern gehen an die anderen Personen
- [x] Reminder für Projektschritte mit Notiz-Fallback bei Urlaubsmodus oder Versandfehler

### Personen, Rollen & Sichtbarkeit

- [x] Personen aus Home Assistant automatisch laden
- [x] Angemeldeten Nutzer über Home Assistant Ingress erkennen
- [x] Admin-Rolle in der UI verwalten
- [x] Rollen: Elternteil, Kind, Haushaltshilfe und Mitglied
- [x] Rollenbasierte Sichtbarkeit für Aufgaben und Raumansichten
- [x] Räume pro Person individuell ausblendbar
- [x] Persönliche Einstellungen auf `/settings`
- [x] Admin-Bereich für Personen, Rollen, Räume und Geräte
- [x] Persönlicher Urlaubsmodus in den Einstellungen
- [x] Urlaubsmodus pausiert fällige Aufgaben und tägliche Benachrichtigungen

### Design & Bedienung

- [x] Responsive Web-UI über Home Assistant Ingress
- [x] Light/Dark Mode über Design-Tokens
- [x] Ruhiger Home-Assistant-naher Look mit Mauve/Rose als Akzent
- [x] Kompakte Aufgaben- und Projektlisten
- [x] OpenMoji-Icons für Aufgaben, Räume und Projekte
- [x] Icon-Auswahl mit manueller Auswahl und automatischer Erkennung
- [x] SVG-Aktionsbuttons, Filter-Chips und Empty States
- [x] Gemeinsame Render-Helfer für Aufgabenzeilen, Projektzeilen und Projektschritte

### Home Assistant Integration

- [x] Add-on läuft über Home Assistant Ingress
- [x] Sidebar-Eintrag auch für Nicht-Admin-Benutzer sichtbar
- [x] Räume aus Home Assistant Area Registry
- [x] Personen aus Home Assistant Persons
- [x] Notify-Services aus Home Assistant
- [x] `SUPERVISOR_TOKEN` für API-Zugriff

### Technik

- [x] FastAPI + uvicorn
- [x] TinyDB-Persistenz unter `/data/tidyhome.json`
- [x] Docker-Build mit Home-Assistant-Base-Image
- [x] Schlanke Modulstruktur mit Routen pro Bereich
- [x] Statisches Stylesheet `assets/app.css`
- [x] Lokale OpenMoji-SVGs als Asset-Fallback
- [x] `CHANGELOG.md` für Home-Assistant-Update-Dialog
- [x] Unit-Tests für Reminder-Logik, Urlaubsmodus-Fallback und Render-Helfer

---

## Geplante Features

### Nächste sinnvolle Schritte

- [ ] Einkaufsliste als eigener Bereich ohne Intervall
- [ ] Aufgaben-Pausen: einzelne Aufgaben temporär einfrieren
- [ ] Kalenderstreifen mit Wochenübersicht
- [ ] HA-Sensoren/Entities für Aufgabenstatus
- [ ] Daten-Export als CSV/JSON-Backup

### Später

- [ ] Fotos pro Aufgabe, Projekt und Schritt
- [ ] Aufgaben-Vorlagen für wiederkehrende Sets
- [ ] Tags oder Kategorien zusätzlich zu Räumen
- [ ] Aufgabenabhängigkeiten, z. B. Vorgänger/Nachfolger
- [ ] REST-API zum Anlegen von Aufgaben per Home-Assistant-Automation
- [ ] Mehrsprachigkeit Deutsch/Englisch

### Ideen

- [idee] Fokus-Modus mit nur wenigen Aufgaben pro Tag
- [idee] Sanfte Sprache für überfällige Aufgaben
- [idee] Energielevel-Modus nach Aufwand und Tagesform
- [idee] Positive Verstärkung nach Erledigung
- [idee] Abzeichen und Achievements
- [idee] Persönliche Verlaufsseite
- [idee] Haushaltshilfe-Zeiterfassung, Stundensatz, Kostenübersicht und CSV-Export
- [idee] Trash-Card-/Müllkalender-Integration als Aufgaben-Trigger
