## 1.2.0

- Dashboard: "Nächste Aufgaben" nutzt jetzt dasselbe Design wie die Aufgabenliste
  (Icon-Bubble, Status-Badge Überfällig/Heute/Geplant, Wichtig-Stern, 1×-Badge)
- Dashboard: Raumlinks und "Erledigt"-Formulare verwenden absolute Ingress-URLs (kein 404 mehr)

## 1.1.9

- Header: Admin-Pill ist jetzt ein echtes Dropdown-Menue mit "Mein Profil",
  "Person wechseln" und "Admin-Bereich"
- Header: Glocke und Drei-Punkte-Menue entfernt (waren ohne Funktion)

## 1.1.8

- Admin-Bereich erreichbar: neuer Button "Admin-Bereich öffnen" auf der Einstellungsseite (nur für Admins sichtbar)
- Bisher musste die URL /admin manuell eingegeben werden — über HA Ingress kaum möglich

## 1.1.7

- Fix: Admin-Panel lädt jetzt wieder zuverlässig (Icon-Chooser durch kompaktes Select ersetzt)
- Rollen können nur noch durch Admins vergeben werden, nicht durch die Personen selbst
- Admin: Raum-Icons pro Raum individuell zuweisbar über Dropdown (gilt für alle Personen)

## 1.1.6

- Admin: Raum-Icons pro Raum individuell zuweisbar (gilt für alle Personen)
- Fix: Admin-Panel und Einstellungen ("Wer bin ich?") mit absoluten URLs repariert
- Fix: Speichern-Weiterleitung im Admin-Panel landet immer mit Erfolgsmeldung

## 1.1.5

- Raum-Icons: OpenMoji-Illustrationen für Küche, Wohnzimmer, Schlafzimmer, Bad, Flur und mehr
- Aufgabenliste: mehr vertikaler Abstand zwischen den Zeilen

## 1.1.4

- Fix: Schritte hinzufügen, abhaken und löschen in Projekten funktionieren wieder
- Fix: Projekt bearbeiten und Zurück-Navigation in der Detailansicht repariert
- Ursache: relative URLs kollidierten mit dem HA-Ingress base-href

## 1.1.3

- OpenMoji Icons: 44 farbige Illustrationen für Haushalts- und Familienaufgaben
- Icon-Chooser: manuelle Icon-Auswahl in Aufgaben- und Projekt-Formularen (🔮 = automatisch)
- Projekte nutzen jetzt ebenfalls OpenMoji-Bubbles statt SVG-Pfaden
- Keyword-Erkennung stark erweitert: Haustiere, Kinder, Auto, Reparatur, Garten u.v.m.

## 1.1.2

- Aufgaben: 3-Zeilen-Layout (Name+Badge / Datum / Aktionen), klarere Dichte auf Mobile
- Aufgaben: Badge-Semantik überarbeitet – "Geplant" / "Heute" / "Überfällig" + separates Timing
- Dashboard: Ring-Charts als einzelne Karten statt gemeinsame Box
- Formular: "Zugewiesen an" full-width, SVG-Stern statt Emoji, 1×-Badge, Back-Button

## 1.1.1

- CSS nach assets/app.css ausgelagert (bessere Performance, saubereres Dark Mode)
- Ring-Charts, SVG-Icons und Card-Layouts vollständig integriert und zusammengeführt
- Aufgaben: Kategorie-Icons und "Meine"-Filter hinzugefügt
- Empty States mit Icon und Hinweistext

## 1.1.0

- Visuelles Redesign: SVG-Icons statt Emoji in Navigation und Aktionsbuttons
- Dashboard: Ring-Charts (Erledigt / Überfällig / Zustand) statt Zahlen-Grid
- Dashboard: "Nächste Aufgaben"-Liste direkt auf der Startseite
- Dashboard: Räume als kompakte Liste mit Icon und Pfeil
- Aufgaben: Kategorie-Icons pro Aufgabe (Staubsauger, Mülleimer, Pflanze etc.)
- Aufgaben: "Meine"-Filter zeigt nur eigene Aufgaben
- Aufgaben: Icon-Buttons für Erledigt/Bearbeiten/Löschen (konsistentes Design)
- Projekte: Card-Layout mit Raumicon, Fortschrittsbalken und Icon-Buttons
- Leerer-Zustand-Seiten mit illustrierter Meldung
- Dark Mode: deutlich verbesserte Kontraste und Farbvariablen

## 1.0.10

- Aufgaben können mehreren Personen gleichzeitig zugeordnet werden
- Mehrfachauswahl per Checkbox in der Aufgaben-Maske
- Eltern/Admins sehen im Raum-Filter Aufgaben nach jeder zugewiesenen Person gruppiert
- Rückwärtskompatibel: bestehende Einzelzuweisungen werden automatisch migriert

## 1.0.9

- Neue Aufgaben werden automatisch dem angemeldeten Nutzer zugeordnet
- Rollen-System: Elternteil / Kind / Haushaltshilfe / Mitglied (im Admin-Panel vergeben)
- Elternteile sehen im Raum-Filter alle Aufgaben nach Person gruppiert
- Kinder können optional Aufgaben anderer Kinder sehen (Berechtigung per Admin)
- Mitglieder und Haushaltshilfen sehen nur eigene und nicht zugeordnete Aufgaben

## 1.0.8

- Fix: Admin-Personenpicker öffnet sich korrekt beim Klick auf den Namen

## 1.0.7

- Person wird automatisch anhand des HA-Logins erkannt (kein manuelles Auswählen mehr nötig)
- Admins können per Klick auf den Namen zwischen Personen wechseln
- Nicht-Admins sehen direkt ihre eigene Ansicht ohne Auswahlmöglichkeit
- Einstellungen anderer Personen nur noch im Admin-Panel sichtbar
- Person bleibt beim Navigieren zwischen Seiten erhalten

## 1.0.6

- Dark Mode: folgt automatisch dem System-/HA-Theme
- Persönliche Statistik auf der Punkte-Seite: Streak, diese Woche, Gesamt-Punkte
- Wochenziel: in den Einstellungen konfigurierbar, Fortschrittsbalken auf der Punkte-Seite
- Eigene Zeile im Leaderboard wird farblich hervorgehoben

## 1.0.5

- Einmalige Aufgaben: nach Erledigung automatisch archiviert (1×-Badge in der Liste)
- Räume pro Person ausblenden: individuelle Raumauswahl in den Einstellungen
- Benachrichtigungen enthalten jetzt auch offene Projektschritte der Person
- Raumkarten auf dem Dashboard berücksichtigen ausgeblendete Räume

## 1.0.4

- Wichtig-Flag fuer Aufgaben: Stern-Badge und orange Markierung, wichtige Aufgaben werden zuerst angezeigt
- Projekte werden automatisch als abgeschlossen markiert, sobald alle Schritte erledigt sind
- Abgeschlossene Projekte erscheinen in einem eigenen Tab mit Archivieren-Button
- Leaderboard mit Tabs: Gesamt / Dieser Monat / Letzter Monat
- Admin-Verwaltung per Checkbox (HA-Personen) statt Freitext in der Konfiguration
- Notify-Services werden automatisch aus Home Assistant geladen und koennen per Checkbox aktiviert werden

## 1.0.3

- Admin-Verwaltung und Geraete-Verwaltung per Checkbox-UI in den Einstellungen
- Notify-Services automatisch aus HA-API befuellt
- Logo als echtes PNG (icon.png) fuer die Add-on-Store-Anzeige

## 1.0.2

- Logo und Favicon integriert
- Startseite mit Uebersicht und Schnellzugriff

## 1.0.1

- Punkte-System mit Leaderboard
- Benachrichtigungen per HA Notify-Service konfigurierbar
- Personen-Einstellungen (Dienste, Benachrichtigungszeit)

## 1.0.0

- Aufgaben mit Intervallen, Raeumen und Punkten
- Projekte mit Schritten und Fortschrittsanzeige
- Raumfilter und Personenzuweisung
- Punkte-Leaderboard
