# TidyHome – Feature-Liste

Alle Anforderungen und Ideen. Status: ✅ umgesetzt · 🔄 in Arbeit · 📋 geplant · 💡 Idee

---

## Aufgaben

- ✅ Aufgaben anlegen (Name, Raum, Intervall, Person, Punkte)
- ✅ Aufgaben bearbeiten
- ✅ Aufgaben löschen
- ✅ Aufgaben abhaken (erledigt markieren)
- ✅ Wiederkehrende Intervalle (täglich bis jährlich)
- ✅ Fälligkeitsanzeige (überfällig / heute / bald / ok) mit Farbkodierung
- ✅ Filter nach Raum, Person, Überfällig
- 📋 Einmalige Aufgaben (kein Intervall, nach Erledigung archiviert)
- 📋 Wichtig-Flag (hervorgehoben in der Liste)
- 📋 Aufwand-Feld (gering / mittel / hoch)
- 📋 Startdatum wählbar
- 📋 Kalenderstreifen (Wochenübersicht mit Aufgaben pro Tag)
- 💡 Fotos pro Aufgabe (Hinweisfoto wo/was, Vorher/Nachher bei Erledigung)
- 💡 Aufgaben-Vorlagen (häufige Sets speichern, z.B. "Frühjahrsputz")
- 💡 Fälligkeit manuell verschieben (einmalige Ausnahme ohne Intervall zu ändern)
- 💡 Aufgaben verknüpfen (Vorgänger/Nachfolger, z.B. erst lüften dann putzen)
- 💡 Tags / Kategorien zusätzlich zu Räumen

## Ordnungsprojekte

- ✅ Projekte anlegen (Name, Raum, Person, Beschreibung)
- ✅ Projekte bearbeiten und löschen
- ✅ Teilschritte hinzufügen (Name, Punkte)
- ✅ Teilschritte abhaken mit Personenzuordnung
- ✅ Fortschrittsbalken pro Projekt
- ✅ Teilschritte löschen
- 📋 Projekte archivieren wenn alle Schritte erledigt
- 💡 Fotos pro Projekt und Schritt (Vorher/Nachher, Hinweisfotos)

## Gamification & Punkte

- ✅ Punkte bei Aufgaben-Erledigung
- ✅ Punkte bei Projektschritte-Erledigung
- ✅ Bestenliste (Gesamt)
- ✅ Getrennte Statistik: Haushaltsaufgaben vs. Projektschritte
- 📋 Bestenliste nach Zeitraum (Monat / Letzter Monat / Gesamt)
- 💡 Wochenziele pro Person (z.B. 5 Aufgaben / Woche)
- 💡 Abzeichen / Achievements (erste Aufgabe, 10er-Serie, Monatsbester …)
- 💡 Persönliche Statistik-Seite (Verlauf, Streak, Lieblingsraum)

## Benachrichtigungen

- ✅ Tägliche Push-Benachrichtigung mit fälligen Aufgaben
- ✅ Per-Person konfigurierbar (eigene Uhrzeit, eigene Geräte)
- ✅ Mehrere Geräte pro Person (kommagetrennt)
- ✅ Admin definiert Geräte, Nutzer stellt Uhrzeit selbst ein
- ✅ Test-Benachrichtigung direkt aus der UI
- 📋 Benachrichtigung auch für Projekte mit offenen Schritten
- 💡 Erinnerung an andere Person schicken ("Küche ist noch offen")

## Benutzerverwaltung & Einstellungen

- ✅ Personen aus Home Assistant geladen
- ✅ Admin-Rolle in Add-on-Konfiguration festlegbar
- ✅ Admins verwalten Geräte-Zuordnung
- ✅ Jeder Nutzer stellt eigene Benachrichtigungszeit ein
- 📋 Urlaubsmodus (Intervalle einfrieren, keine Notifications)
- 💡 Räume pro Person individuell ausblenden (z.B. Kinderzimmer nur für Eltern sichtbar)

## Barrierefreiheit & Neurodiversität

- 💡 Fokus-Modus: reduzierte Ansicht mit nur 1–3 Aufgaben pro Tag (für ADHS / Reizüberflutung)
- 💡 Sanfte Sprache: keine negativen Formulierungen bei überfälligen Aufgaben ("noch offen" statt "überfällig")
- 💡 Energielevel-Modus: Aufgaben nach Aufwand filtern (gering / mittel / hoch) je nach Tagesverfassung
- 💡 Aufgaben-Pausen: Intervalle temporär einfrieren ohne Urlaubsmodus (z.B. bei depressiven Episoden)
- 💡 Positive Verstärkung: ermutigende Meldungen bei Erledigung, keine Straf-Mechanismen
- 💡 Erinnerungsabstand anpassen: sanftere Benachrichtigungsfrequenz pro Person einstellbar
- 💡 Strukturhilfe: Aufgaben automatisch in kleine Teilschritte vorschlagen (gut für Autismus / ADHS)

## Familie & Kommunikation

- 💡 Kommentare / Notizen zu Aufgaben und Projekten hinterlassen
- 💡 Einkaufsliste als eigener Bereich (ähnlich wie Projekte, ohne Intervall)

## Design & Navigation

- ✅ Responsive Web-UI über HA Ingress
- ✅ Farbkodierung nach Dringlichkeit
- ✅ Redesign: Warm-Rose/Mauve Farbschema (Betidy-Stil)
- ✅ Bottom-Navigation (Zuhause / Aufgaben / Projekte / Punkte / Einstellungen)
- ✅ Dashboard (Zuhause): Begrüßung, Tagesstatistik, Raumkarten-Grid
- ✅ Aufgabenliste auf /tasks (Dashboard wird neue Startseite)
- ✅ Raumkarten mit Fortschrittsbalken und Aufgaben/Projekt-Anzahl
- 💡 Dunkles / Helles Design (Dark Mode / Light Mode umschaltbar, folgt optional HA-Theme)

## Home Assistant Integration

- ✅ Räume aus HA Area Registry (Template-API)
- ✅ Personen aus HA Persons
- ✅ Notify-Services aus HA (mobile_app, alexa, etc.)
- ✅ SUPERVISOR_TOKEN für API-Auth
- 📋 HA-Sensoren/Entities für Aufgabenstatus (optional, für Automationen)
- 💡 Verknüpfung mit Trash Card (Müllkalender-Karte als Aufgaben-Trigger)
- 💡 Aufgaben per HA-Automation anlegen (REST-API Endpunkt)

## Technisch

- ✅ TinyDB-Persistenz unter /data
- ✅ FastAPI + uvicorn
- ✅ HA Ingress-kompatible Navigation (X-Ingress-Path)
- ✅ Docker-Build mit HA Base-Image
- ✅ Dual-Remote Git (Gitea + GitHub)
- ✅ Automatischer Versionierungsworkflow
- 💡 Mehrsprachigkeit (Deutsch / Englisch)
- 💡 Daten-Export (CSV / JSON-Backup der gesamten Datenbank)
