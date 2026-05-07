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
- ✅ Badge-Semantik: "Geplant" / "Heute" / "Überfällig" als Status; Timing separat ("Morgen", "In 3 Tagen")
- ✅ Kategorie-Icons pro Aufgabe (nach Name/Raum automatisch vergeben)
- ✅ Filter nach Raum, Person, Überfällig, Meine, Aufwand
- ✅ Wichtig-Flag (Stern-Badge, orange Markierung, wird oben sortiert)
- ✅ Einmalige Aufgaben (nach Erledigung automatisch archiviert, 1×-Badge)
- ✅ Neue Aufgaben automatisch dem angemeldeten Nutzer zugeordnet
- ✅ Aufgaben mehreren Personen gleichzeitig zuweisbar (Mehrfach-Checkbox)
- ✅ Aufwand-Feld (wenig / mittel / viel) mit Badge und Filter
- ✅ Startdatum wählbar (Aufgabe erst ab diesem Datum sichtbar und fällig)
- ✅ Fälligkeit einmalig verschieben (Snooze) ohne Intervall zu ändern
- 📋 Aufgaben-Pausen: Intervalle temporär einfrieren
- 📋 Kalenderstreifen (Wochenübersicht mit Aufgaben pro Tag)
- 💡 Fotos pro Aufgabe (Hinweisfoto wo/was, Vorher/Nachher bei Erledigung)
- 💡 Aufgaben-Vorlagen (häufige Sets speichern, z.B. "Frühjahrsputz")
- 💡 Aufgaben verknüpfen (Vorgänger/Nachfolger, z.B. erst lüften dann putzen)
- 💡 Tags / Kategorien zusätzlich zu Räumen

## Ordnungsprojekte

- ✅ Projekte anlegen (Name, Raum, Person, Beschreibung)
- ✅ Projekte bearbeiten und löschen
- ✅ Schritte hinzufügen, abhaken und löschen
- ✅ Teilschritte hinzufügen (Name, Punkte)
- ✅ Teilschritte abhaken mit Personenzuordnung
- ✅ Fortschrittsbalken pro Projekt
- ✅ Teilschritte löschen
- ✅ Projekte automatisch abschließen wenn alle Schritte erledigt
- ✅ Abgeschlossene Projekte in eigenem Tab mit Archivieren-Button
- 💡 Fotos pro Projekt und Schritt (Vorher/Nachher, Hinweisfotos)

## Gamification & Punkte

- ✅ Punkte bei Aufgaben-Erledigung
- ✅ Punkte bei Projektschritte-Erledigung
- ✅ Bestenliste (Gesamt / Dieser Monat / Letzter Monat)
- ✅ Getrennte Statistik: Haushaltsaufgaben vs. Projektschritte
- ✅ Persönliche Statistik: Streak 🔥, Punkte diese Woche, Gesamt-Punkte
- ✅ Wochenziel pro Person konfigurierbar mit Fortschrittsbalken
- ✅ Eigene Zeile im Leaderboard hervorgehoben
- 💡 Abzeichen / Achievements (erste Aufgabe, 10er-Serie, Monatsbester …)
- 💡 Persönliche Verlaufsseite (Aktivitätshistorie, Lieblingsraum)

## Benachrichtigungen

- ✅ Tägliche Push-Benachrichtigung mit fälligen Aufgaben
- ✅ Offene Projektschritte in der täglichen Benachrichtigung
- ✅ Per-Person konfigurierbar (eigene Uhrzeit, eigene Geräte)
- ✅ Admin definiert Geräte (Notify-Services per Checkbox aus HA)
- ✅ Test-Benachrichtigung direkt aus der UI
- 💡 Erinnerung an andere Person schicken ("Küche ist noch offen")
- 💡 Urlaubsmodus (keine Notifications, Intervalle eingefroren)

## Benutzerverwaltung & Rollen

- ✅ Personen aus Home Assistant geladen
- ✅ Automatische Erkennung des angemeldeten Nutzers via HA-Login
- ✅ Admin-Rolle per Checkbox in der UI (Personen aus HA)
- ✅ Admins können Ansicht für andere Personen öffnen (▾-Pill)
- ✅ Rollen-System: Elternteil / Kind / Haushaltshilfe / Mitglied
- ✅ Rollenbasierte Sichtbarkeit:
  - Elternteil/Admin: alle Aufgaben, nach Person gruppiert im Raum-View
  - Kind mit Berechtigung: eigene + andere Kinder
  - Mitglied/Haushaltshilfe: nur eigene + nicht zugeordnete
- ✅ Räume pro Person individuell ausblendbar
- ✅ Persönliche Einstellungen auf /settings, alle Personen im Admin-Panel
- 📋 Urlaubsmodus (Intervalle einfrieren, keine Notifications)

## Haushaltshilfe

- ✅ Rolle "Haushaltshilfe" vergeben (durch Admin)
- 💡 Zeiterfassung: Arbeitsbeginn / -ende pro Einsatz eintragen oder stempeln
- 💡 Stundensatz hinterlegen (durch Admin, nicht sichtbar für die Haushaltshilfe)
- 💡 Kostenübersicht für Admins: Stunden × Stundensatz pro Monat / Zeitraum
- 💡 Aufgaben-Protokoll: welche Aufgaben wurden in welchem Einsatz erledigt
- 💡 Export der Zeiterfassung (CSV) für Abrechnung oder Steuererklärung

## Familie & Kommunikation

- 📋 Kommentare / Notizen zu Aufgaben und Projekten hinterlassen
- 📋 Erinnerung senden: andere Person auf offene Aufgabe hinweisen
- 📋 Einkaufsliste als eigener Bereich (ähnlich wie Projekte, ohne Intervall)
- 📋 Urlaubsmodus: Intervalle einfrieren, keine Notifications

## Barrierefreiheit & Neurodiversität

- 💡 Fokus-Modus: reduzierte Ansicht mit nur 1–3 Aufgaben pro Tag (für ADHS / Reizüberflutung)
- 💡 Sanfte Sprache: keine negativen Formulierungen bei überfälligen Aufgaben
- 💡 Energielevel-Modus: Aufgaben nach Aufwand filtern je nach Tagesverfassung
- 💡 Aufgaben-Pausen: Intervalle temporär einfrieren (z.B. bei depressiven Episoden)
- 💡 Positive Verstärkung: ermutigende Meldungen bei Erledigung
- 💡 Strukturhilfe: Aufgaben automatisch in kleine Teilschritte vorschlagen

## Design & Navigation

- ✅ Responsive Web-UI über HA Ingress
- ✅ Farbkodierung nach Dringlichkeit
- ✅ Warm-Rose/Mauve Farbschema
- ✅ Bottom-Navigation (Zuhause / Aufgaben / Projekte / Punkte / Einstellungen)
- ✅ Dashboard: Begrüßung, Tagesstatistik, Raumkarten
- ✅ Dashboard: Schnellaktions-Buttons "+ Aufgabe" und "+ Projekt"
- ✅ Dashboard: Räume gefiltert nach eigenen Aufgaben/Projekten; fremde Räume für Admins/Eltern abgesetzt
- ✅ Dark Mode (folgt automatisch System-/HA-Theme)
- ✅ Person bleibt beim Navigieren zwischen Seiten erhalten
- ✅ Modern UI Refresh: ruhiger, Home-Assistant-näherer Look
- ✅ Design-Tokens für Light/Dark Mode
- ✅ Externes Stylesheet assets/app.css; FOUC-Fix via inline Critical CSS
- ✅ Dashboard: Ring-Charts (Erledigt/Überfällig/Zustand) als einzelne Karten
- ✅ Aufgabenliste: kompaktes Layout, Badge-Semantik, OpenMoji-Icons, SVG-Aktions-Buttons
- ✅ Icon-Chooser im Formular: manuelle Auswahl oder automatische Erkennung
- ✅ Projektkarten mit sichtbarem Fortschritt
- ✅ Filter als kompakte Chip-Leiste
- ✅ Empty States mit Icon und Hinweistext
- 📋 Abzeichen / Achievements

## Home Assistant Integration

- ✅ Räume aus HA Area Registry
- ✅ Personen aus HA Persons
- ✅ Notify-Services aus HA (mobile_app, alexa, etc.)
- ✅ SUPERVISOR_TOKEN für API-Auth
- ✅ Automatische Nutzer-Erkennung via HA Ingress-Header
- 📋 HA-Sensoren/Entities für Aufgabenstatus (für Automationen)
- 💡 Verknüpfung mit Trash Card (Müllkalender-Karte als Aufgaben-Trigger)
- 💡 Aufgaben per HA-Automation anlegen (REST-API Endpunkt)

## Technisch

- ✅ TinyDB-Persistenz unter /data
- ✅ FastAPI + uvicorn
- ✅ HA Ingress-kompatible Navigation (X-Ingress-Path)
- ✅ Docker-Build mit HA Base-Image
- ✅ Dual-Remote Git (Gitea + GitHub)
- ✅ CHANGELOG.md für HA Update-Dialog
- ✅ Statisches Stylesheet assets/app.css mit lokalem Asset-Fallback
- 💡 Mehrsprachigkeit (Deutsch / Englisch)
- 💡 Daten-Export (CSV / JSON-Backup der gesamten Datenbank)
