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

## Benachrichtigungen

- ✅ Tägliche Push-Benachrichtigung mit fälligen Aufgaben
- ✅ Per-Person konfigurierbar (eigene Uhrzeit, eigene Geräte)
- ✅ Mehrere Geräte pro Person (kommagetrennt)
- ✅ Admin definiert Geräte, Nutzer stellt Uhrzeit selbst ein
- ✅ Test-Benachrichtigung direkt aus der UI
- 📋 Benachrichtigung auch für Projekte mit offenen Schritten

## Benutzerverwaltung & Einstellungen

- ✅ Personen aus Home Assistant geladen
- ✅ Admin-Rolle in Add-on-Konfiguration festlegbar
- ✅ Admins verwalten Geräte-Zuordnung
- ✅ Jeder Nutzer stellt eigene Benachrichtigungszeit ein
- 📋 Urlaubsmodus (Intervalle einfrieren, keine Notifications)
- 💡 Räume pro Person ausblenden (z.B. Kinderzimmer nur für Eltern sichtbar)

## Design & Navigation

- ✅ Responsive Web-UI über HA Ingress
- ✅ Farbkodierung nach Dringlichkeit
- ✅ Redesign: Warm-Rose/Mauve Farbschema (Betidy-Stil)
- ✅ Bottom-Navigation (Zuhause / Aufgaben / Projekte / Punkte / Einstellungen)
- ✅ Dashboard (Zuhause): Begrüßung, Tagesstatistik, Raumkarten-Grid
- ✅ Aufgabenliste auf /tasks (Dashboard wird neue Startseite)
- ✅ Raumkarten mit Fortschrittsbalken und Aufgaben/Projekt-Anzahl

## Home Assistant Integration

- ✅ Räume aus HA Area Registry (Template-API)
- ✅ Personen aus HA Persons
- ✅ Notify-Services aus HA (mobile_app, alexa, etc.)
- ✅ SUPERVISOR_TOKEN für API-Auth
- 📋 HA-Sensoren/Entities für Aufgabenstatus (optional, für Automationen)
- 💡 Verknüpfung mit Trash Card (Müllkalender-Karte als Aufgaben-Trigger)

## Technisch

- ✅ TinyDB-Persistenz unter /data
- ✅ FastAPI + uvicorn
- ✅ HA Ingress-kompatible Navigation (X-Ingress-Path)
- ✅ Docker-Build mit HA Base-Image
- ✅ Dual-Remote Git (Gitea + GitHub)
- ✅ Automatischer Versionierungsworkflow
