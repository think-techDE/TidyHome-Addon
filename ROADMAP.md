# TidyHome - Roadmap

Stand: 2026-05-09 · Aktuelle Version: 1.3.34

Diese Roadmap trennt den aktuellen Stand von den nächsten sinnvollen Ausbauschritten. Historische Phasen sind zusammengefasst, damit die nächsten Entscheidungen schneller sichtbar sind.

---

## Aktueller Stand

TidyHome ist aktuell ein nutzbares Home-Assistant-Add-on für:

- wiederkehrende und einmalige Haushaltsaufgaben
- persönliche Aufgabenansichten mit Rollen und Sichtbarkeit
- Ordnungsprojekte mit Schritten, Fortschritt und Punkten
- Kommentare und Notizen an Aufgaben und Projekten
- Vorher/Nachher-Fotos an Aufgaben, Projekten und Projektschritten
- Erinnerungen an andere Personen und Projektschritte
- tägliche Benachrichtigungen über Home Assistant Notify-Services
- persönlichen Urlaubsmodus
- Punkte, Bestenliste, Erfolgshistorie, Streak und Wochenziel
- mobile Web-UI über Home Assistant Ingress

Die Codebasis ist inzwischen modularisiert:

- `main.py` enthält App-Setup, Router und Healthcheck
- `routes/` enthält Dashboard, Aufgaben, Projekte, Punkte und Einstellungen
- `render.py` enthält Layout, Navigation und gemeinsame Render-Helfer
- `storage.py` bündelt TinyDB-Zugriff und Geschäftslogik
- `reminders.py` und `scheduler.py` trennen manuelle Reminder von täglichen Benachrichtigungen

---

## Zuletzt erledigt

### v1.3.34

- Neue Aufgaben können direkt beim Erstellen eine erste Notiz speichern
- Erstellnotizen werden als normale Aufgaben-Notizen abgelegt

### v1.3.33

- Notizen-Karten sind wie Foto-Karten einklappbar
- Leerer Notizen-Zustand kompakter gestaltet

### v1.3.32

- Einmalige Aufgaben sind jetzt Standard im Intervall-Dropdown
- Aufgaben-Historie für erledigte und archivierte Aufgaben ergänzt
- Erledigte Aufgaben können aus der Historie bearbeitet und wieder aktiviert werden

### v1.3.31

- Dashboard zeigt unter „Nächste Aufgaben“ nur noch heutige und überfällige Aufgaben
- Neue Aufgaben benachrichtigen zugewiesene Personen automatisch über die konfigurierten Notify-Services

### v1.3.30

- Datei-Upload bleibt dauerhaft als eigener Button neben der Kameraaufnahme verfügbar
- Foto-Hinweistext trennt Kameraaufnahme und Datei-Upload klarer

### v1.3.29

- Versteckte Foto-Fallback-Buttons werden durch eine explizite `[hidden]`-Regel zuverlässig ausgeblendet
- Foto-Aktionsleiste zeigt sichtbare Buttons einspaltig und vermeidet doppelte Kamera-Aktionen

### v1.3.28

- Fotoaufnahme zeigt im Normalfall nur noch die Live-Kamera-Aktion
- Datei- und Native-Fallbacks werden erst sichtbar, wenn die WebView die Live-Kamera nicht bereitstellt oder blockiert

### v1.3.27

- Kamera-Fallback nutzt ein echtes Datei-/Kamera-Label statt programmatischem Klick
- Upload-Routen akzeptieren Live-Kamera-, native Kamera- und Datei-Uploads getrennt

### v1.3.26

- Kamera-Button fällt bei WebViews ohne direkte Kamera-API automatisch auf den nativen Kamera-/Dateidialog zurück

### v1.3.25

- Fotoaufnahme wieder als echte Live-Kamera mit Vorschau umgesetzt
- Kamera-Snapshot wird über das normale Upload-Formular gespeichert
- Datei-Auswahl bleibt als getrennter Fallback sichtbar

### v1.3.24

- Foto-Button öffnet direkt den nativen Kamera-/Dateidialog
- Fotoformular sendet nach Bildauswahl automatisch ab

### v1.3.23

- Fotoaufnahme auf den nativen Kamera-/Dateidialog umgestellt
- Direkte Live-Kameraansicht entfernt, damit Fotos auch für Nicht-Admin-Benutzer im Home-Assistant-Panel zuverlässig funktionieren

### v1.3.22

- Foto-Indikatoren in Aufgaben-, Projekt- und Schrittzeilen ergänzt
- Foto-Karten sind einklappbar und öffnen automatisch, wenn Fotos vorhanden sind

### v1.3.21

- Mobile Aufgabenzeilen gegen Überlagerungen von Titel, Status und Aktionen optimiert
- Aktionsicons rutschen auf schmalen Displays in eine eigene Zeile

### v1.3.20

- Live-Kameraaufnahme mit Vorschau für Vorher/Nachher-Fotos ergänzt
- Kamera-Snapshot wird direkt an die bestehenden Foto-Routen hochgeladen
- Datei-Upload bleibt als Fallback erhalten

### v1.3.19

- Foto-Uploads öffnen auf Smartphones bevorzugt die Kamera
- Vorher/Nachher-Fotos bleiben weiterhin als normaler Datei-Upload nutzbar

### v1.3.18

- Vorher/Nachher-Fotos für Aufgaben ergänzt
- Vorher/Nachher-Fotos für Projekte und einzelne Projektschritte ergänzt
- Fotoablage unter `/data/photos` mit statischer Auslieferung über `/photos`

### v1.3.17

- Punktebereich um Verlauf der letzten Erfolge ergänzt
- Erfolgsmeldung mit Punktzahl nach erledigten Aufgaben und Projektschritten
- Score-Log speichert neue Erfolge mit Aufgaben-/Schrittnamen

### v1.3.16

- Bottom-Navigation auf lokale OpenMoji-Icons umgestellt
- README, Feature-Liste und Roadmap neu geordnet

### v1.3.15

- Projektliste zeigt offene Schritte bei anderen Personen direkt an
- Personenmenü in Kopfzeile übersichtlicher gegliedert
- Render-Tests für Aufgabenzeile, Projektzeile und Projektschritt-Zeile ergänzt

### v1.3.14

- Reminder-Unit-Tests für Empfängerlogik, Versandnotiz, Urlaubsmodus-Fallback und Projektschritte ergänzt
- Projektzeile, Projektschritt-Zeile und Projektschritt-Erinnerungsformular in gemeinsame Render-Helfer ausgelagert

### v1.3.13

- Erfolgsmeldung nach Reminder-Versand ergänzt
- Notiztexte verständlicher formuliert
- Erinnerungen für Projekt-Schritte umgesetzt
- Gemeinsame Aufgabenzeilen-Komponente für Zuhause und Aufgabenliste eingeführt

### v1.3.10 bis v1.3.12

- Persönlicher Urlaubsmodus in den Einstellungen
- Aufgaben bleiben sichtbar, werden aber bei Fälligkeit und Benachrichtigung pausiert
- Notizen zu Aufgaben und Projekten
- Erinnerungsglocke nur, wenn andere Empfänger vorhanden sind
- Erinnerungsglocke auch auf Zuhause sichtbar, wenn sinnvoll

---

## Nächster Fokus

### 1. Einkaufsliste

Ziel: Gemeinsame Liste für Besorgungen ohne Intervall-Logik.

- eigener Bereich in der Bottom-Navigation oder unter Aufgaben
- Einträge hinzufügen, abhaken, löschen
- optional Person, Menge und Notiz
- keine Punkte, keine Fälligkeit, kein Intervall
- später optional Kategorien wie Supermarkt, Drogerie, Baumarkt

Warum jetzt: Die App hat inzwischen stabile Personen-, Notiz- und Listenmuster. Eine Einkaufsliste kann diese Muster nutzen, ohne die Aufgabenlogik weiter aufzublähen.

### 2. Aufgaben-Pausen

Ziel: Einzelne Aufgaben temporär einfrieren, unabhängig vom persönlichen Urlaubsmodus.

- Pause direkt an einer Aufgabe setzen
- optionales Enddatum
- pausierte Aufgaben sichtbar lassen
- Badge "Pausiert"
- nicht als fällig zählen
- tägliche Benachrichtigung ignoriert pausierte Aufgaben

Abgrenzung: Urlaubsmodus pausiert die Person. Aufgaben-Pause pausiert genau eine Aufgabe.

### 3. Wochenübersicht

Ziel: Besser sehen, was in den nächsten Tagen ansteht.

- kompakter Kalenderstreifen in Aufgaben oder Zuhause
- Tage mit Anzahl fälliger Aufgaben
- Wechsel zwischen heute, morgen und Woche
- keine vollständige Kalender-App

### 4. Home-Assistant-Entities

Ziel: TidyHome stärker automatisierbar machen.

- Sensor für offene Aufgaben
- Sensor für heutige Aufgaben
- Sensor für überfällige Aufgaben
- optional pro Person
- später Automationen auf Basis dieser Sensoren

### 5. Export & Backup

Ziel: Daten leichter sichern und auswerten.

- JSON-Export der gesamten TinyDB
- CSV-Export für Aufgaben, Projekte, Punkte
- Import zunächst nicht priorisieren

---

## Spätere Ausbaustufen

### Foto-Ausbau

- optionaler Bildvergleich für Vorher/Nachher

### Aufgaben-Vorlagen

- häufige Sets speichern, z. B. Frühjahrsputz
- mehrere Aufgaben auf einmal erzeugen
- Standardräume, Intervalle und Punkte übernehmen

### Kategorien & Abhängigkeiten

- Tags zusätzlich zu Räumen
- Aufgaben verknüpfen, z. B. erst lüften, dann putzen
- optionale Sortierung nach Abhängigkeiten

### Haushaltshilfe-Verwaltung

- Zeiterfassung pro Einsatz
- Stundensatz nur für Admins sichtbar
- Kostenübersicht pro Monat oder Zeitraum
- CSV-Export für Abrechnung

### Barrierefreiheit & Neurodiversität

- Fokus-Modus mit 1 bis 3 Aufgaben pro Tag
- sanftere Sprache bei überfälligen Aufgaben
- Energielevel-Modus nach Aufwand
- positive Rückmeldungen nach Erledigung

---

## Historisch abgeschlossen

- Ordnungsprojekte mit Projekt- und Step-Modellen
- Punkte für Aufgaben und Projektschritte
- Dashboard als Zuhause-Ansicht
- Bottom-Navigation
- moderne kompakte UI mit Light/Dark Mode
- Rollenmodell und Home-Assistant-Login-Erkennung
- persönliche Einstellungen und Admin-Bereich
- Raum-/Personenverwaltung aus Home Assistant
- Notify-Service-Auswahl und tägliche Push-Benachrichtigung
- OpenMoji-Icon-System für Aufgaben, Räume und Projekte
- Refactoring in Routen, Speicherlogik und Render-Helfer
