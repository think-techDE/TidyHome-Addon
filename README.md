# TidyHome

> Haushalt organisieren, verteilen und gamifizieren — direkt in Home Assistant.

![Version](https://img.shields.io/badge/version-1.0.1-b5738a)
![HA](https://img.shields.io/badge/Home%20Assistant-Add--on-41bdf5)

Inspiriert von [Betidy](https://betidy.io/). TidyHome bringt strukturiertes Haushaltsmanagement als natives HA-Add-on: Aufgaben mit Intervallen, Ordnungsprojekte mit Teilschritten, Punkte für die ganze Familie und Push-Benachrichtigungen — alles über Ingress direkt im HA-Dashboard.

---

## Features

### Aufgaben
- Aufgaben anlegen mit Raum, Intervall (täglich bis jährlich), Person und Punkte
- Fälligkeitsanzeige mit Farbkodierung (überfällig / heute / bald / ok)
- Filter nach Raum, Person oder Überfällig
- Aufgaben bearbeiten, löschen und abhaken

### Ordnungsprojekte
- Projekte mit Teilschritten verwalten (z.B. "Keller aufräumen")
- Fortschrittsbalken pro Projekt
- Punkte pro erledigtem Schritt

### Gamification
- Punkte bei jeder erledigten Aufgabe und jedem Projektschritt
- Bestenliste für die ganze Familie
- Getrennte Statistik: Haushaltsaufgaben vs. Projektschritte

### Benachrichtigungen
- Tägliche Push-Benachrichtigung mit fälligen Aufgaben
- Pro Person konfigurierbar: eigene Uhrzeit, eigene Geräte (mobile_app, Alexa …)
- Test-Benachrichtigung direkt aus der UI

### Benutzerverwaltung
- Personen und Räume automatisch aus Home Assistant geladen
- Admin-Rolle in der Add-on-Konfiguration festlegbar
- Admins verwalten Geräte, jeder Nutzer stellt seine Uhrzeit selbst ein

### Design
- Warm-Rose/Mauve Farbschema
- Responsive Web-UI mit Bottom-Navigation (5 Tabs)
- Dashboard mit Tagesstatistik und Raumkarten-Grid

---

## Installation

1. **HA → Einstellungen → Add-ons → Add-on-Store → ⋮ → Benutzerdefinierte Repositories**
2. Repository-URL eintragen:
   ```
   https://github.com/think-techDE/TidyHome-Addon
   ```
3. **TidyHome** installieren und starten
4. In der Add-on-Konfiguration optional Admins eintragen:
   ```yaml
   admins: "Danny,Marina"
   ```

---

## Konfiguration

| Option | Typ | Beschreibung |
|---|---|---|
| `log_level` | `info` \| `debug` \| `warning` … | Log-Detail-Grad |
| `admins` | String (kommagetrennt) | Personen mit Admin-Rechten (Geräteverwaltung) |

---

## Projektstruktur

```
tidyhome/
  app/
    main.py          # App-Setup, Router, Startup
    config.py        # ADMINS, Logger
    render.py        # HTML/CSS-Template, Hilfsfunktionen
    scheduler.py     # Benachrichtigungslogik
    routes/
      dashboard.py   # GET /
      tasks.py       # GET/POST /tasks/*
      projects.py    # GET/POST /projects/*
      scores.py      # GET /scores
      settings.py    # /settings, /admin, /notify-now
    models.py        # Pydantic-Modelle
    storage.py       # TinyDB-Datenbankschicht
    ha_client.py     # Home Assistant API-Client
  assets/
    logo.svg         # App-Logo
  config.yaml        # Add-on-Metadaten
  Dockerfile
  run.sh
```

Daten werden unter `/data/tidyhome.json` persistiert (TinyDB).

---

## Links

- [Feature-Liste](FEATURES.md)
- [Roadmap](ROADMAP.md)
- [Gitea Repository](https://git.think-tech.eu/Danny/TidyHome-Addon)
