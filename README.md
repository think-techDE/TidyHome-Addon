# TidyHome

> Haushalt ruhig organisieren, fair verteilen und motivierend erledigen - direkt in Home Assistant.

![Version](https://img.shields.io/badge/version-1.1.7-b5738a)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--on-41bdf5)

TidyHome ist ein Home-Assistant-Add-on für wiederkehrende Haushaltsaufgaben, gemeinsame Ordnungsprojekte, Punkte und persönliche Erinnerungen. Die App läuft über Home Assistant Ingress und ist für die schnelle Nutzung auf Smartphone, Tablet und Dashboard gedacht.

Der Fokus liegt auf Übersicht statt Druck: Was ist heute wichtig? Was ist überfällig? Wer ist zuständig? Welche Projekte kommen voran? TidyHome bündelt diese Antworten in einer ruhigen Oberfläche mit Light/Dark Mode, klaren Fälligkeiten und einer mobilen Bottom-Navigation.

---

## Highlights

- Aufgaben mit Raum, Intervall, Personenzuordnung, Punkten und Wichtig-Flag
- Mehrfachzuweisung an mehrere Personen
- Einmalige und wiederkehrende Aufgaben
- Ordnungsprojekte mit Teilschritten, Fortschritt und Punkten
- Bestenliste und persönliche Statistik mit Streak, Wochenpunkten und Wochenziel
- Tägliche Push-Benachrichtigungen pro Person und Gerät
- Rollen für Elternteil, Kind, Haushaltshilfe und Mitglied
- Automatische Personen- und Raumintegration aus Home Assistant
- Responsive Web-UI über Home Assistant Ingress

---

## Design-Richtung

TidyHome soll sich wie ein ruhiges Werkzeug im Home-Assistant-Umfeld anfühlen: klar, kompakt und freundlich, ohne verspielt zu wirken.

- Neutrale Flächen mit Mauve/Rose als wiedererkennbarem Akzent
- Gemeinsame Design-Tokens für Light und Dark Mode
- Dashboard als Heute-Ansicht mit Status, nächsten Aufgaben und Raumüberblick
- Aufgabenlisten mit klaren Fälligkeits-Badges und schnellen Icon-Aktionen
- Projektkarten mit sichtbarem Fortschritt und nächstem Schritt
- Filter als kompakte Chip-Leiste
- Gute Lesbarkeit, ausreichende Touch-Ziele und reduzierte Schatten

Der Modern UI Refresh ist umgesetzt; die nächsten Feinschliffe sind in [FEATURES.md](FEATURES.md) und [ROADMAP.md](ROADMAP.md) beschrieben.

---

## Funktionen

### Aufgaben

- Aufgaben anlegen, bearbeiten, löschen und abhaken
- Intervalle von täglich bis jährlich
- Einmalige Aufgaben, die nach Erledigung automatisch archiviert werden
- Fälligkeit nach Status: überfällig, heute, bald oder ok
- Filter nach Raum, Person und Überfälligkeit
- Wichtig-Flag für priorisierte Aufgaben

### Ordnungsprojekte

- Projekte mit Raum, Person und Beschreibung
- Teilschritte mit eigenen Punkten
- Fortschrittsbalken pro Projekt
- Automatischer Abschluss, wenn alle Schritte erledigt sind
- Abgeschlossene Projekte in eigener Ansicht

### Punkte & Motivation

- Punkte für erledigte Aufgaben und Projektschritte
- Bestenliste für Gesamt, aktuellen Monat und letzten Monat
- Getrennte Auswertung für Haushaltsaufgaben und Projektschritte
- Persönliche Statistik mit Streak, Wochenpunkten und Wochenziel

### Benachrichtigungen

- Tägliche Erinnerung an fällige Aufgaben
- Offene Projektschritte in der täglichen Benachrichtigung
- Eigene Uhrzeit und Geräte pro Person
- Notify-Services aus Home Assistant auswählbar
- Test-Benachrichtigung direkt aus der UI

### Rollen & Sichtbarkeit

- Personen aus Home Assistant werden automatisch geladen
- Angemeldeter Nutzer wird über Home Assistant Ingress erkannt
- Admins können Personen, Rollen, Räume und Geräte verwalten
- Rollenbasierte Sichtbarkeit für Elternteil, Kind, Haushaltshilfe und Mitglied
- Räume können pro Person individuell ausgeblendet werden

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

## Projektstruktur

```text
tidyhome/
  app/
    main.py          # App-Setup, Router, Startup
    config.py        # Konfiguration und Logger
    render.py        # HTML-Template und Render-Helfer
    scheduler.py     # Benachrichtigungslogik
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
- [Gitea Repository](https://git.think-tech.eu/Danny/TidyHome-Addon)
