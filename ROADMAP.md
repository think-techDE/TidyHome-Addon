# TidyHome - Roadmap

Stand: 2026-05-10 · Aktuelle Version: 1.3.52

Diese Roadmap trennt den aktuellen Stand von den nächsten sinnvollen Ausbauschritten. Historische Phasen sind zusammengefasst, damit die nächsten Entscheidungen schneller sichtbar sind.

---

## Aktueller Stand

TidyHome ist aktuell ein nutzbares Home-Assistant-Add-on für:

- wiederkehrende und einmalige Haushaltsaufgaben
- pausierbare Aufgaben mit Wochenübersicht und Tagesfilter
- Aufgaben-Vorlagen zum schnellen Erstellen ähnlicher Aufgaben
- persönliche Aufgabenansichten mit Rollen und Sichtbarkeit
- Ordnungsprojekte mit Schritten, Fortschritt und Punkten
- Kommentare und Notizen an Aufgaben und Projekten
- Vorher/Nachher-Fotos an Aufgaben, Projekten und Projektschritten
- Erinnerungen an andere Personen und Projektschritte
- tägliche Benachrichtigungen über Home Assistant Notify-Services
- persönlichen Urlaubsmodus
- Haushaltshilfe-Zeiterfassung mit Lohnhistorie, Monatsabrechnung, Status und Export
- Punkte, Bestenliste, Achievements, persönliche Verlaufsauswertung, Streak und Wochenziel
- mehrsprachige UI in Deutsch, Englisch, Französisch und Spanisch
- JSON-Backup, CSV-Exporte und Admin-Diagnose
- mobile Web-UI über Home Assistant Ingress

Die Codebasis ist inzwischen modularisiert:

- `main.py` enthält App-Setup, Router und Healthcheck
- `routes/` enthält Dashboard, Aufgaben, Projekte, Punkte und Einstellungen
- `render.py` enthält Layout, Navigation und gemeinsame Render-Helfer
- `ui_cards.py` enthält Foto- und Notizkarten
- `ui_icons.py` enthält OpenMoji-/SVG-Icon-Daten und Icon-Renderer
- `ui_rows.py` enthält Aufgaben-, Projekt- und Projektschrittzeilen
- `translations/` enthält i18n-Quelltexte und Sprachkataloge
- `storage.py` bündelt TinyDB-Zugriff und Geschäftslogik
- `reminders.py` und `scheduler.py` trennen manuelle Reminder von täglichen Benachrichtigungen

---

## Zuletzt erledigt

### v1.3.52

- Aufgaben-, Projekt- und Projektschrittzeilen aus `render.py` in `ui_rows.py` ausgelagert
- Bestehende `render.task_row`-, `render.project_row`- und Schritt-Renderzugriffe kompatibel gehalten
- Syntaxprüfung und vollständige Unit-Test-Suite erneut validiert

### v1.3.51

- Foto- und Notizkarten aus `render.py` in `ui_cards.py` ausgelagert
- Bestehende `render.comments_card`- und `render.photos_card`-Zugriffe kompatibel gehalten
- Foto-/Notiztests und vollständige Unit-Test-Suite erneut validiert

### v1.3.50

- Icon-Daten und Icon-Renderer aus `render.py` in `ui_icons.py` ausgelagert
- Bestehende Render-Importe kompatibel gehalten, damit Routen unverändert funktionieren
- Tests nach dem Renderer-Split erneut validiert

### v1.3.49

- i18n-Datei verschlankt und Übersetzungsquellen in eigene Module ausgelagert
- Sprachkataloge für Englisch, Französisch und Spanisch separat strukturiert
- Tests nach der Modulaufteilung erneut validiert

### v1.3.48

- Scores, Haushaltshilfe-Verwaltung, Projektformulare, Aufgabenformularbereiche und Admin-Kernflächen weiter auf i18n-Schlüssel umgestellt
- Wörterbuch für Punkte, Haushaltshilfen, Projekt-/Aufgabenformulare und Admin-Texte in Englisch, Französisch und Spanisch erweitert
- Tests nach der erweiterten i18n-Abdeckung erneut validiert

### v1.3.47

- i18n von globaler Textersetzung auf explizite UI-Schlüssel umgestellt
- Navigation, Dashboard, Aufgaben-/Projektzeilen, Foto-/Notizkarten und zentrale Einstellungen auf Schlüssel vorbereitet
- Freie Inhalte wie Aufgaben-, Raum-, Projekt- und Personennamen bleiben sprachunabhängig unverändert
- Tests für explizite UI-Übersetzung und unveränderte freie Inhalte ergänzt

### v1.3.46

- Automatische Sprachwahl wertet `Accept-Language` inklusive `q`-Werten aus
- Admins behalten beim Betrachten anderer Personen ihre eigene UI-Sprache
- HTML-Antworten liefern nun `Content-Language`
- Tests für automatische Sprachwahl und Admin-Personenwechsel ergänzt

### v1.3.45

- Mehrsprachige UI für Deutsch, Englisch, Französisch und Spanisch ergänzt
- Sprache pro Person in den Einstellungen auswählbar
- Automatische Spracherkennung über Browser-/Home-Assistant-Sprache ergänzt
- Server-Rendering läuft durch eine zentrale i18n-Schicht

### v1.3.44

- Aufgaben-Pausen mit optionalem Enddatum und Grund umgesetzt
- Wochenübersicht mit Tagesfilter in der Aufgabenliste ergänzt
- Aufgaben-Vorlagen mit Speichern, Bearbeiten, Löschen und Erstellen aus Vorlage umgesetzt
- Achievements für persönliche Meilensteine ergänzt
- Persönliche Verlaufsseite mit Wochen- und Monatsentwicklung ergänzt
- Admin-Bereich um JSON-Backup, CSV-Export und Daten-Diagnose erweitert

### v1.3.43

- Monatsabrechnung pro Haushaltshilfe mit Status offen, geprüft und bezahlt ergänzt
- CSV- und PDF-Export pro Haushaltshilfe und Monat umgesetzt
- Stundensatz-Historie nachträglich korrigierbar gemacht
- Schnellbuttons für Heute, Start jetzt, Ende jetzt und Pausenvorlagen ergänzt
- Bezahlte Monate für Haushaltshilfen als Nur-Lesen-Ansicht umgesetzt
- Warnhinweise bei fehlendem oder nicht passendem Stundensatz ergänzt

### v1.3.42

- Arbeitszeit-Erfassung im Haushaltshilfe-Bereich einklappbar gemacht
- Stundensatz- und Lohnhistorie pro Haushaltshilfe in einen kompakten Ausklappbereich verschoben

### v1.3.41

- Stundensätze für Haushaltshilfen als Historie mit gültig-ab und optionalem gültig-bis Datum gespeichert
- Monatskosten werden pro Arbeitseintrag mit dem am Arbeitstag gültigen Stundensatz berechnet
- Lohnhistorie im Haushaltshilfe-Bereich sichtbar gemacht

### v1.3.40

- Haushaltshilfe-Verwaltung von der Zuhause-Startseite für Eltern/Admins entfernt
- Einstieg bleibt im Personenmenü unter Haushaltshilfen

### v1.3.39

- Personenmenü um direkten Bereich für Haushaltshilfen ergänzt
- Zuhause unterscheidet zwischen Verwaltern und Haushaltshilfen: Eltern/Admins sehen die Verwaltung, Haushaltshilfen ihre persönliche Arbeitszeit

### v1.3.38

- Haushaltshilfe-Dashboard für Eltern/Admins ergänzt
- Stundenlohn pro Haushaltshilfe speicherbar
- Arbeitszeiten pro Einsatz erfassbar, korrigierbar und löschbar
- Monatsübersicht mit Stunden und Gesamtkosten ergänzt
- Haushaltshilfen sehen auf Zuhause ihre Monatsstunden und den bisher erarbeiteten Lohn

### v1.3.37

- Neue Aufgaben können direkt beim Erstellen ein optionales Vorher-Foto erhalten
- Kameraaufnahme und Datei-Auswahl werden beim Erstellen vorgemerkt und zusammen mit der Aufgabe gespeichert

### v1.3.36

- Aufgabenformular neu gegliedert: Aufgabe, Planung, Zuständigkeit und Darstellung
- `Als wichtig markieren` steht jetzt direkt im oberen Aufgabenbereich
- Einstellungen in kompakte Blöcke für Benachrichtigung, Motivation, Urlaub und Räume aufgeteilt
- Admin-Bereich mit Übersichtskarten und Sprungmarken für Rechte, Räume, Geräte und Profile aufgeräumt

### v1.3.35

- Einmalige Aufgaben werden nicht mehr mit einem zusätzlichen `1×`-Badge in Aufgabenlisten markiert

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

## Empfohlene nächste Ausbaustufen

### 1. Einkaufsliste & Besorgungen

Ziel: Besorgungen von Aufgaben trennen, damit Aufgaben sauber bei Haushalt und Projekten bleiben.

- eigener Bereich für Einkaufsliste ohne Intervall, Fälligkeit oder Punkte
- Einträge hinzufügen, abhaken, wieder öffnen und löschen
- Menge, Notiz und optionale Kategorie
- Kategorien wie Supermarkt, Drogerie, Baumarkt, Garten, Apotheke
- wiederkehrende Einkaufsartikel als Vorschläge
- optional später gemeinsame Listen pro Raum oder Projekt

Warum zuerst: Die App wird dadurch im Alltag häufiger geöffnet, ohne die bestehende Aufgabenlogik komplizierter zu machen.

### 2. Aufgaben-Vorlagen 2.0

Ziel: Aus einzelnen Vorlagen echte Aufgabenpakete machen.

- mehrere Aufgaben aus einer Vorlage auf einmal erzeugen
- Vorlagen-Sets für Frühjahrsputz, Gästezimmer, Urlaubsvorbereitung oder Auto
- Standardwerte für Raum, Punkte, Aufwand, Person und Intervall übernehmen
- Vorlagen aus bestehenden Projekten ableiten
- Vorlagen optional als Eltern-/Admin-Funktion schützen

Warum jetzt: Einzelvorlagen sind umgesetzt. Der nächste Nutzen entsteht durch ganze Sets.

### 3. Motivation & gemeinsame Ziele

Ziel: Erfolge sichtbarer machen, ohne Druck aufzubauen.

- Familienziele und Kinderziele
- Belohnungsziele mit frei definierbarem Zielwert
- sanftere Sprache und bessere Gruppierung bei überfälligen Aufgaben
- Energielevel-Modus nach Aufwand und Tagesform
- optionale reduzierte Ansicht ohne Punkte und Wettbewerb

Wichtig: Motivation sollte optional bleiben. Die App darf nicht strafend wirken, wenn Aufgaben liegen bleiben.

### 4. Haushaltshilfen: Abrechnung 2.0

Ziel: Die aktuelle Zeiterfassung revisionssicherer und alltagstauglicher machen.

- freie Von/Bis-Zeitraumfilter zusätzlich zur Monatsansicht
- Zahlungsdatum und Zahlungsnotiz bei bezahlten Monaten
- Korrekturverlauf für Arbeitszeiten und Stundensätze
- Warnungen für fehlende Zeiten, ungewöhnlich lange Einsätze und fehlende Pausen
- Sammelabrechnung für alle Haushaltshilfen eines Monats
- optionaler Foto- oder Beleganhang an Arbeitseinträgen

Warum nicht zuerst: Die Basis ist jetzt nutzbar. Weitere Abrechnungstiefe ist wichtig, aber weniger breit wirksam als Einkaufsliste und Wochenplanung.

### 5. Home Assistant Automation

Ziel: TidyHome stärker in Home Assistant einbinden.

- Sensoren für offene, heutige und überfällige Aufgaben
- optionale Sensoren pro Person
- Kalender-Integration für fällige Aufgaben
- Todo-Integration für Einkaufsliste oder Aufgaben
- REST-API für Automationen, z. B. Aufgabe aus Sensorereignis anlegen
- Müllkalender-/Trash-Card-Integration als Aufgaben-Trigger

### 6. Daten, Import & Wartung

Ziel: Betrieb und Wiederherstellung robuster machen.

- Import-/Wiederherstellungsfunktion
- Backup-Vergleich vor Wiederherstellung
- Admin-Aktionen zur Bereinigung verwaister Fotos und alter Referenzen
- optionale Foto-Bereinigung für gelöschte oder archivierte Einträge
- weitere UI-Sprachen und feinere Übersetzung einzelner Spezialtexte

---

## Spätere Ideen

### Foto-Ausbau

- Galerieansicht pro Aufgabe, Projekt und Person
- optionaler Bildvergleich für Vorher/Nachher
- bessere mobile Vorschau und Bildkomprimierung

### Kategorien & Abhängigkeiten

- Tags zusätzlich zu Räumen
- Aufgaben verknüpfen, z. B. erst lüften, dann putzen
- optionale Sortierung nach Abhängigkeiten
- Blocker-Hinweis, wenn eine Vorgängeraufgabe offen ist

### Barrierefreiheit & Neurodiversität

- Fokus-Modus mit 1 bis 3 Aufgaben pro Tag
- reduzierte Ansicht ohne Punkte und Wettbewerb
- große Touch-Ziele für sehr kleine Displays
- klarere Texte für Kinder und Haushaltshilfen

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
