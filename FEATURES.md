# TidyHome - Features

Stand: 2026-05-10 · Version 1.3.52

Status: `[x]` umgesetzt · `[ ]` geplant · `[idee]` Idee

---

## Kernfunktionen

### Aufgaben

- [x] Aufgaben anlegen, bearbeiten, löschen und erledigen
- [x] Wiederkehrende Intervalle von täglich bis jährlich
- [x] Einmalige Aufgaben als Standard im Intervall-Dropdown
- [x] Einmalige Aufgaben mit automatischer Archivierung nach Erledigung
- [x] Aufgaben-Historie für erledigte und archivierte Aufgaben
- [x] Erledigte Aufgaben aus der Historie bearbeiten und wieder aktivieren
- [x] Startdatum: Aufgaben erst ab einem gewählten Datum sichtbar und fällig
- [x] Fälligkeit einmalig verschieben, ohne das Intervall zu ändern
- [x] Einzelne Aufgaben pausieren, optional mit Enddatum und Grund
- [x] Pausierte Aufgaben bleiben sichtbar, zählen aber nicht als fällig
- [x] Wochenübersicht mit Tagesfilter für anstehende Aufgaben
- [x] Statusanzeige für geplant, heute, überfällig und ok
- [x] Raum, Punkte, Aufwand und Wichtig-Flag pro Aufgabe
- [x] Wichtig-Flag direkt im oberen Bereich des Aufgabenformulars
- [x] Aufgabenformular in Abschnitte für Aufgabe, Planung, Zuständigkeit und Darstellung gegliedert
- [x] Aufgaben-Vorlagen speichern, bearbeiten, löschen und daraus neue Aufgaben erzeugen
- [x] Mehrfachzuweisung an mehrere Personen
- [x] Neue Aufgaben werden standardmäßig der angemeldeten Person zugeordnet
- [x] Dashboard zeigt nur heutige und überfällige Aufgaben unter „Nächste Aufgaben“
- [x] Neue Aufgaben für andere Personen lösen automatisch eine Smartphone-Benachrichtigung aus
- [x] Filter nach Raum, Person, Überfälligkeit und Aufwand
- [x] Kommentare und Notizen direkt an Aufgaben
- [x] Optionale Notiz direkt beim Erstellen neuer Aufgaben
- [x] Einklappbare Notizen-Karten mit kompaktem Leerzustand
- [x] Vorher/Nachher-Fotos direkt an Aufgaben
- [x] Optionales Vorher-Foto direkt beim Erstellen neuer Aufgaben
- [x] Smartphone-Kameraaufnahme und Datei-Upload für Aufgabenfotos
- [x] Foto-Indikator in Aufgabenlisten
- [x] Mobile Aufgabenzeilen mit separater Aktionszeile gegen Überlagerungen
- [x] Erinnerung an andere zugewiesene Personen senden

### Projekte

- [x] Projekte mit Name, Raum, Person, Beschreibung und Icon
- [x] Projektschritte hinzufügen, erledigen und löschen
- [x] Punkte pro Projektschritt
- [x] Fortschrittsbalken pro Projekt
- [x] Automatischer Projektabschluss, wenn alle Schritte erledigt sind
- [x] Abgeschlossene Projekte in eigener Ansicht mit Archivierung
- [x] Kommentare und Notizen direkt an Projekten
- [x] Vorher/Nachher-Fotos an Projekten und einzelnen Projektschritten
- [x] Smartphone-Kameraaufnahme und Datei-Upload für Projekt- und Schritt-Fotos
- [x] Foto-Indikatoren in Projekt- und Schrittansichten
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
- [x] Admins behalten beim Betrachten anderer Personen ihre eigene UI-Sprache
- [x] Überarbeitetes Personenmenü mit klaren Bereichen für Ansicht, Einstellungen und Verwaltung
- [x] Eltern/Admins sehen auf Zuhause den Einstieg zur Haushaltshilfe-Verwaltung
- [x] Haushaltshilfen sehen auf Zuhause Monatsstunden und bisher erarbeiteten Lohn
- [x] Sprache pro Person wählbar oder automatisch aus Browser-/Home-Assistant-Sprache
- [x] Schlüsselbasierte UI-Übersetzung, damit freie Aufgaben-, Raum- und Projektnamen unverändert bleiben
- [x] Punkte-, Projekte-, Aufgabenformular-, Haushaltshilfe- und Admin-Flächen weiter schlüsselbasiert übersetzt

### Punkte & Motivation

- [x] Punkte für erledigte Aufgaben
- [x] Punkte für erledigte Projektschritte
- [x] Bestenliste für Gesamt, aktuellen Monat und letzten Monat
- [x] Eigene Zeile im Leaderboard hervorgehoben
- [x] Getrennte Auswertung für Haushaltsaufgaben und Projektschritte
- [x] Persönliche Statistik mit Streak, Wochenpunkten, Gesamtpunkten und Wochenziel
- [x] Erfolgsmeldung mit Punkten direkt nach dem Erledigen
- [x] Verlauf der letzten Erfolge mit Aufgabe, Datum und Punktzahl
- [x] Achievements für persönliche Meilensteine
- [x] Persönliche Verlaufsseite mit Wochen- und Monatsentwicklung

### Haushaltshilfen

- [x] Haushaltshilfe-Rolle als Basis für Zeiterfassung
- [x] Stundenlohn-Historie pro Haushaltshilfe verwalten
- [x] Stundenlohn-Historie nachträglich korrigieren
- [x] Stundensätze mit gültig-ab und optionalem gültig-bis Datum berechnen
- [x] Einklappbare Bereiche für Arbeitszeit-Erfassung und Stundensatz-Historie
- [x] Arbeitszeiten pro Einsatz erfassen
- [x] Arbeitszeiten nachträglich korrigieren und löschen
- [x] Monatsübersicht mit Stunden und Gesamtkosten
- [x] Monatsabrechnung mit Status offen, geprüft und bezahlt
- [x] CSV- und PDF-Export pro Haushaltshilfe und Monat
- [x] Schnellbuttons für Heute, Start jetzt, Ende jetzt und Pausenvorlagen
- [x] Bezahlte Monate für Haushaltshilfen als Nur-Lesen-Ansicht
- [x] Warnhinweise bei fehlendem oder nicht passendem Stundensatz
- [x] Persönliche Eingabemaske für Haushaltshilfen

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
- [x] Admin-Bereich mit JSON-Backup, CSV-Export und Daten-Diagnose
- [x] Einstellungen mit kompakten Abschnitten für Benachrichtigung, Motivation, Urlaub und Räume
- [x] Admin-Übersicht mit Sprungmarken für Rechte, Räume, Benachrichtigungen und Profile
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
- [x] Icon-Daten und Icon-Renderer aus dem Haupt-Renderer in ein eigenes UI-Modul ausgelagert
- [x] Foto- und Notizkarten aus dem Haupt-Renderer in ein eigenes UI-Modul ausgelagert
- [x] Aufgaben-, Projekt- und Projektschrittzeilen aus dem Haupt-Renderer in ein eigenes UI-Modul ausgelagert
- [x] Mehrsprachige UI in Deutsch, Englisch, Französisch und Spanisch
- [x] `Accept-Language` wird inklusive Qualitätswerten für automatische Sprache ausgewertet

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
- [x] JSON-Backup der TinyDB
- [x] CSV-Export für Aufgaben, Projekte und Punkte
- [x] Admin-Diagnose für verwaiste Personen, Räume, Projektschritte und Fotos
- [x] Zentrale i18n-Schicht für die bestehende serverseitig gerenderte UI
- [x] Übersetzungskataloge nach Quellen und Sprachen in eigenen Modulen getrennt

---

## Geplante Features

### Priorität 1: Alltag schneller machen

- [ ] Einkaufsliste als eigener Bereich ohne Intervall, Fälligkeit oder Punkte
- [ ] Mengen, Notizen und Kategorien für Einkaufsliste, z. B. Supermarkt, Drogerie, Baumarkt
- [ ] Wiederkehrende Einkaufsartikel als Vorschläge, ohne sie automatisch als Aufgabe zu behandeln
- [ ] Tagesfokus mit bewusst kleiner Aufgabenliste für Personen, die nur das Nötigste sehen wollen

### Priorität 2: Aufgaben besser planen

- [ ] Mehrere Aufgaben aus einer Vorlage auf einmal erzeugen
- [ ] Tags oder Kategorien zusätzlich zu Räumen
- [ ] Aufgabenabhängigkeiten, z. B. erst aufräumen, dann saugen
- [ ] optionales Enddatum für Aufgabenserien
- [ ] Aufgaben duplizieren, um ähnliche Aufgaben schneller anzulegen

### Priorität 3: Motivation sichtbarer machen

- [ ] Familienziele, z. B. gemeinsame Wochenpunkte oder erledigte Aufgaben
- [ ] Belohnungsziele für Kinder mit frei definierbaren Zielwerten
- [ ] sanftere Sprache und bessere Gruppierung für überfällige Aufgaben
- [ ] Energielevel-Modus nach Aufwand und Tagesform

### Priorität 4: Haushaltshilfen abrunden

- [ ] Zeitraumfilter mit freiem Von/Bis zusätzlich zur Monatsauswahl
- [ ] Zahlungsnotizen und Zahlungsdatum für bezahlte Abrechnungen
- [ ] Korrekturverlauf für Arbeitszeiten und Stundensätze
- [ ] Plausibilitätsprüfung für fehlende Zeiten, ungewöhnlich lange Einsätze und fehlende Pausen
- [ ] optionaler Export aller Haushaltshilfen eines Monats als Sammelabrechnung

### Priorität 5: Home Assistant stärker nutzen

- [ ] HA-Sensoren für heutige, offene und überfällige Aufgaben
- [ ] optionale Sensoren pro Person
- [ ] Home-Assistant-Kalender-Integration für fällige Aufgaben
- [ ] Home-Assistant-Todo-Integration für Einkaufsliste oder Aufgaben
- [ ] REST-API zum Anlegen von Aufgaben per Automation
- [ ] Müllkalender-/Trash-Card-Integration als Aufgaben-Trigger

### Priorität 6: Daten & Betrieb

- [ ] Import-/Wiederherstellungsfunktion für TidyHome-Daten
- [ ] Admin-Aktionen zum Bereinigen verwaister Fotos oder alter Referenzen
- [ ] optionale automatische Foto-Bereinigung für gelöschte oder archivierte Einträge
- [ ] weitere UI-Sprachen und feinere Übersetzung einzelner Admin-Spezialtexte
