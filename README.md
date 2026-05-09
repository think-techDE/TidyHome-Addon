# TidyHome

> Haushalt ruhig organisieren, fair verteilen und motivierend erledigen - direkt in Home Assistant.

![Version](https://img.shields.io/badge/version-1.3.33-b5738a)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--on-41bdf5)

TidyHome ist ein Home-Assistant-Add-on für wiederkehrende Haushaltsaufgaben, gemeinsame Ordnungsprojekte, Punkte und persönliche Erinnerungen. Die App läuft über Home Assistant Ingress und ist für die schnelle Nutzung auf Smartphone, Tablet und Dashboard gedacht.

Der Fokus liegt auf Übersicht statt Druck: Was ist heute wichtig? Was ist überfällig? Wer ist zuständig? Welche Projekte kommen voran? TidyHome bündelt diese Antworten in einer ruhigen Oberfläche mit Light/Dark Mode, klaren Fälligkeiten und einer mobilen Bottom-Navigation.

---

## Highlights

- Aufgaben mit Raum, Intervall, Personenzuordnung, Punkten, Aufwand und Wichtig-Flag
- Dashboard zeigt unter „Nächste Aufgaben“ nur heutige und überfällige Aufgaben
- Mehrfachzuweisung an mehrere Personen
- Einmalige Aufgaben als Standard sowie wiederkehrende Aufgaben
- Aufgaben-Historie zum Bearbeiten und Wieder-Aktivieren erledigter Aufgaben
- Ordnungsprojekte mit Teilschritten, Fortschritt, Punkten und Hinweisen auf offene Schritte bei anderen Personen
- Notizen zu Aufgaben und Projekten
- Einklappbare Notizen-Karten mit kompaktem Leerzustand
- Vorher/Nachher-Fotos für Aufgaben, Projekte und einzelne Projektschritte
- Erinnerungen an zugewiesene Personen und Projekt-Schritte, inklusive Notiz-Fallback
- Automatische Benachrichtigung, wenn eine Aufgabe für eine andere Person erstellt wird
- Aufgaben-, Raum- und Projekt-Icons mit OpenMoji-Auswahl und automatischer Erkennung
- Bestenliste, Erfolgshistorie und persönliche Statistik mit Streak, Wochenpunkten und Wochenziel
- Tägliche Push-Benachrichtigungen pro Person und Gerät
- Persönlicher Urlaubsmodus zum Pausieren fälliger Aufgaben und Benachrichtigungen
- Rollen für Elternteil, Kind, Haushaltshilfe und Mitglied
- Automatische Personen- und Raumintegration aus Home Assistant
- Responsive Web-UI über Home Assistant Ingress

---

## Aktueller Fokus

Die Basisfunktionen sind nutzbar. Die nächsten sinnvollen Ausbauschritte sind:

1. Einkaufsliste als einfacher gemeinsamer Bereich ohne Intervall
2. Aufgaben-Pausen für einzelne Aufgaben, getrennt vom Urlaubsmodus
3. Wochenübersicht für anstehende Aufgaben
4. Home-Assistant-Entities für Automationen
5. Export und Backup der gespeicherten Daten

Details stehen in [ROADMAP.md](ROADMAP.md).

---

## Design-Richtung

TidyHome soll sich wie ein ruhiges Werkzeug im Home-Assistant-Umfeld anfühlen: klar, kompakt und freundlich, ohne verspielt zu wirken.

- Neutrale Flächen mit Mauve/Rose als wiedererkennbarem Akzent
- Gemeinsame Design-Tokens für Light und Dark Mode
- Dashboard als Heute-Ansicht mit Status, nächsten Aufgaben und Raumüberblick
- Aufgabenlisten mit klaren Fälligkeits-Badges und schnellen Icon-Aktionen
- Mobile Aufgabenzeilen mit getrenntem Inhalts- und Aktionsbereich
- Projektkarten mit sichtbarem Fortschritt und Hinweisen auf offene Schritte
- Erweiterte OpenMoji-Iconauswahl für Aufgaben, Räume und Projekte
- Bottom-Navigation mit lokalen OpenMoji-Icons
- Filter als kompakte Chip-Leiste
- Gute Lesbarkeit, ausreichende Touch-Ziele und reduzierte Schatten

---

## Funktionen

### Aufgaben

- Aufgaben anlegen, bearbeiten, löschen und abhaken
- Notizen direkt an Aufgaben hinterlegen, einklappbar wie Fotos
- Erinnerungen an zugewiesene Personen senden, mit Notiz-Fallback
- Automatische Benachrichtigung bei neu zugewiesenen Aufgaben
- Intervalle von einmalig bis jährlich
- Einmalige Aufgaben als Standard im Intervall-Dropdown, nach Erledigung automatisch archiviert
- Historie erledigter Aufgaben mit Bearbeiten und Wieder-Aktivieren
- Startdatum und einmaliges Verschieben der Fälligkeit
- Fälligkeit nach Status: überfällig, heute, bald oder ok
- Filter nach Raum, Person, Überfälligkeit und Aufwand
- Wichtig-Flag für priorisierte Aufgaben
- Vorher/Nachher-Fotos direkt an der Aufgabe
- Fotoaufnahme per Smartphone-Kamera oder Datei-Upload
- Foto-Indikator in Aufgabenlisten, wenn Fotos vorhanden sind

### Ordnungsprojekte

- Projekte mit Raum, Person, Beschreibung und Icon
- Teilschritte mit eigenen Punkten und eigener Zuständigkeit
- Notizen direkt am Projekt sammeln
- Vorher/Nachher-Fotos am Projekt und an einzelnen Schritten
- Smartphone-Kameraaufnahme auch für Projekt- und Schritt-Fotos
- Foto-Indikatoren in Projekt- und Schrittansichten
- Erinnerungen an zuständige Projektschritte senden, mit Notiz-Fallback
- Projektliste zeigt, wenn offene Schritte bei anderen Personen liegen
- Projekt-Icons aus Aufgaben- und Raum-/Orts-Icons auswählbar
- Fortschrittsbalken pro Projekt
- Automatischer Abschluss, wenn alle Schritte erledigt sind
- Abgeschlossene Projekte in eigener Ansicht

### Punkte & Motivation

- Punkte für erledigte Aufgaben und Projektschritte
- Bestenliste für Gesamt, aktuellen Monat und letzten Monat
- Getrennte Auswertung für Haushaltsaufgaben und Projektschritte
- Persönliche Statistik mit Streak, Wochenpunkten und Wochenziel
- Sichtbare Erfolgsmeldung nach Erledigung mit vergebenen Punkten
- Verlauf der letzten Erfolge mit Aufgabe, Datum und Punktzahl

### Benachrichtigungen

- Tägliche Erinnerung an fällige Aufgaben
- Offene Projektschritte in der täglichen Benachrichtigung
- Eigene Uhrzeit und Geräte pro Person
- Notify-Services aus Home Assistant auswählbar
- Test-Benachrichtigung direkt aus der UI
- Persönlicher Urlaubsmodus pausiert fällige Aufgaben und Benachrichtigungen bis zum gewählten Datum

### Rollen & Sichtbarkeit

- Personen aus Home Assistant werden automatisch geladen
- Angemeldeter Nutzer wird über Home Assistant Ingress erkannt
- Der Home-Assistant-Sidebar-Eintrag ist auch für Nicht-Admin-Benutzer sichtbar
- Admins können Personen, Rollen, Räume und Geräte verwalten
- Raum-Icons im Admin-Bereich per visueller Auswahl konfigurierbar
- Rollenbasierte Sichtbarkeit für Elternteil, Kind, Haushaltshilfe und Mitglied
- Räume können pro Person individuell ausgeblendet werden
- Personenmenü mit klar getrennten Bereichen für Ansicht, Einstellungen und Verwaltung

---

## Installation

1. In Home Assistant zu **Einstellungen > Add-ons > Add-on-Store** wechseln.
2. Über das Menü **Benutzerdefinierte Repositories** öffnen.
3. Repository-URL eintragen:

   ```text
   https://github.com/think-techDE/TidyHome-Addon
   ```

4. **TidyHome** installieren und starten.
5. Die Web-UI über den Add-on-Ingress öffnen.

---

## Konfiguration

| Option | Typ | Beschreibung |
|---|---|---|
| `log_level` | `debug` / `info` / `warning` / `error` / `critical` | Log-Detailgrad |
| `admins` | String, kommagetrennt | Initiale Admin-Personen, optional |

Admin- und Geräteeinstellungen können anschließend direkt in der TidyHome-Oberfläche verwaltet werden.

---

## Entwicklung

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Weitere lokale Prüfung:

```powershell
.\.venv\Scripts\python.exe -m py_compile tidyhome\app\main.py tidyhome\app\render.py tidyhome\app\routes\dashboard.py tidyhome\app\routes\tasks.py tidyhome\app\routes\projects.py tidyhome\app\routes\settings.py tidyhome\app\routes\scores.py
git diff --check
```

---

## Projektstruktur

```text
tidyhome/
  app/
    main.py          # App-Setup, Router, Startup
    config.py        # Konfiguration und Logger
    render.py        # HTML-Layout, Navigation und Render-Helfer
    reminders.py     # Manuelle Erinnerungen
    scheduler.py     # Tägliche Benachrichtigungen
    routes/
      dashboard.py   # Startseite
      tasks.py       # Aufgaben
      projects.py    # Ordnungsprojekte
      scores.py      # Punkte und Statistik
      settings.py    # Einstellungen, Admin, Benachrichtigungstest
    models.py        # Pydantic-Modelle
    storage.py       # TinyDB-Datenbankschicht
    ha_client.py     # Home Assistant API-Client
  assets/
    app.css          # Light/Dark Design-System
    logo.svg         # App-Logo
    icons/           # lokale OpenMoji-SVGs
  config.yaml        # Add-on-Metadaten
  Dockerfile
  run.sh
```

Daten werden unter `/data/tidyhome.json` persistiert.

---

## Links

- [Feature-Liste](FEATURES.md)
- [Roadmap](ROADMAP.md)
- [Changelog](tidyhome/CHANGELOG.md)
- [GitHub Repository](https://github.com/think-techDE/TidyHome-Addon)
