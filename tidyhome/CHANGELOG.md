## 1.3.13

- Erinnerung: Erfolgsmeldung nach Versand oder Notiz-Fallback anzeigen
- Erinnerung: Notiztexte verständlicher formulieren, z. B. "Danny hat Petra erinnert"
- Projekte: Erinnerung an zuständige Person eines offenen Projektschritts senden
- Refactoring: gemeinsame Aufgabenzeilen-Komponente für Zuhause und Aufgabenliste
- Doku: README, Feature-Liste und Roadmap aktualisiert

## 1.3.12

- Aufgaben: Erinnerungs-Glocke erscheint nur, wenn andere zugewiesene Personen erinnert werden können
- Zuhause: Erinnerungs-Glocke auch in der nächsten Aufgabenliste anzeigen
- Erinnerung: Bei Aufgaben mit mehreren Zugewiesenen automatisch alle anderen Personen erinnern

## 1.3.11

- Aufgaben: Erinnerung an zugewiesene Personen senden; bei fehlendem Gerät oder Versandfehler wird eine Notiz hinterlegt
- Refactoring: Notiz-/Kommentar-Karte für Aufgaben und Projekte vereinheitlicht
- Doku: README, Feature-Liste und Roadmap aktualisiert

## 1.3.10

- Neu: persönlicher Urlaubsmodus in den Einstellungen mit optionalem Enddatum
- Urlaubsmodus: Aufgaben bleiben sichtbar und erhalten den Status "Pausiert"
- Urlaubsmodus: pausierte Aufgaben zählen nicht als heute fällig oder überfällig
- Urlaubsmodus: tägliche Push-Benachrichtigungen und Test-Benachrichtigungen werden unterdrückt
- UI: Hinweisbanner und Personenkarte zeigen den aktiven Urlaubsmodus mit deutschem Datum
- Neu: Notizen zu Aufgaben und Projekten mit Autor und Zeitstempel
- Aufgaben: Notizen sind in der Bearbeiten-Ansicht sichtbar und ergänzbar
- Projekte: Notizen sind in der Detailansicht sichtbar und ergänzbar
- Doku: README, Feature-Liste und Roadmap aktualisiert

## 1.3.9

- Neu: globaler Urlaubsmodus im Admin-Bereich mit optionalem Enddatum
- Urlaubsmodus: fällige Aufgaben werden pausiert und tauchen nicht in Heute/Überfällig auf
- Urlaubsmodus: tägliche Push-Benachrichtigungen und Test-Benachrichtigungen werden unterdrückt
- UI: globaler Hinweisbanner zeigt aktiven Urlaubsmodus in allen Ansichten
- Doku: README, Feature-Liste und Roadmap aktualisiert

## 1.3.8

- Punkte: persönlicher Fortschrittsbereich mit Rang, Wochenziel und motivierendem Zielhinweis
- Punkte: Erfolgs-Kacheln für Wochenpunkte, Streak, Monatsrang, Aufgaben, Projektschritte und Gesamtpunkte
- Bestenliste: modernisierte Darstellung mit Rangkreis, hervorgehobener eigener Zeile und klarer Quellenaufschlüsselung
- Punkte: Zeitraum-Zusammenfassung zeigt Gesamtpunkte, Erledigungen und aktuelle Spitze

## 1.3.7

- Aufgaben: redundanten Filter "Meine" entfernt, weil die Standardansicht bereits persönliche Aufgaben zeigt
- Aufgaben: Filterleiste ist dadurch kürzer und fachlich eindeutiger

## 1.3.6

- Aufgaben: Listenansicht mit Dashboard-nahem Kopfbereich und kompakten Statuskacheln für Heute, spät/offen und geplant
- Projekte: Listenansicht mit Dashboard-nahem Kopfbereich, Fortschrittskacheln und moderneren Projektzeilen
- Projekte: Fortschritt, Status und Metadaten sind in der Liste klarer scanbar
- Projektformulare: neue und bearbeitete Projekte nutzen konsistente Seitenköpfe mit Zurück-Aktion

## 1.3.5

- Aufgabenliste: Fälligkeit steht jetzt direkt hinter dem Aufgabennamen statt in einer eigenen Kalenderzeile
- Dashboard: "Nächste Aufgaben" nutzt dieselbe kompakte Namenszeile wie die Aufgabenliste
- UI: redundante Personenanzeige in persönlichen Aufgabenlisten entfernt

## 1.3.4

- UI: Icon-Picker in Aufgaben-/Projektformularen und im Admin-Bereich sind jetzt durchsuchbar
- UI: Große Icon-Auswahlen sind auf eine feste Höhe begrenzt und scrollbar
- Aufgabenliste: Aufwand-Badge steht jetzt unter dem Status-Badge; Status bleibt ohne Aufwand vertikal mittig
- Dashboard: "Nächste Aufgaben" nutzt dieselbe Aufgabenzeilen-Darstellung wie die Aufgabenliste inklusive Aufwand, Status und Aktionsbuttons

## 1.3.3

- Admin: Raum-Icon-Auswahl um weitere OpenMoji-Symbole für Räume, Orte, Reisen, Tiere und Hobbybereiche erweitert
- Raum-Icons: automatische Erkennung bleibt konservativ, erkennt aber passende Raumbezeichnungen auch als Teilstring
- Projekte: Icon-Auswahl bietet jetzt Aufgaben-Icons und Raum-/Orts-Icons gemeinsam an
- Projekte: automatische Projekt-Icons nutzen die gleiche Raum-Erkennung wie der Admin-Bereich
- Doku: README, Feature-Liste und Roadmap auf den aktuellen Icon-Stand gebracht

## 1.3.2

- Fix: Aufwand-Auswahl im Aufgabenformular ist jetzt klickbar und zeigt die aktive Auswahl direkt an
- Aufwand: vierte Option heißt jetzt "Ohne" und bleibt der Standard für neue Aufgaben
- Doku: überflüssigen Hinweis für alte Installationen entfernt

## 1.3.1

- Fix: Home-Assistant-Sidebar-Eintrag ist jetzt auch für Nicht-Admin-Benutzer sichtbar (`panel_admin: false`)
- Fix: interne App-Version wieder mit Add-on-Version synchronisiert

## 1.3.0

- Neu: Aufwand-Feld pro Aufgabe (Wenig / Mittel / Viel) – Badge in der Zeile, Filter-Chip in der Liste
- Neu: Startdatum fuer Aufgaben – Aufgabe erst ab diesem Datum sichtbar und faellig
- Neu: Faelligkeit einmalig verschieben (Snooze) – Schnell-Seite mit +1/+3/+7/+14/+30 Tage oder eigenem Datum
- Neu: Snooze-Button direkt in der Aufgabenzeile; Verschiebung wird nach Erledigung automatisch aufgehoben
- Neu: "Verschoben bis"-Badge und Datumstext wenn eine Aufgabe gesnoozed ist
- Doku: FEATURES.md und ROADMAP.md auf aktuellen Stand gebracht

## 1.2.10

- Fix: Leere Seite nach Update behoben (html opacity:0 verhinderte Darstellung; jetzt nur body)
- Dashboard: Schnellaktions-Buttons "+ Aufgabe" und "+ Projekt" direkt auf der Startseite
- Dashboard: Raeume nur noch sichtbar wenn Person eigene Aufgaben oder Projekte darin hat
- Dashboard: Admins und Elternteile sehen fremde Raeume abgesetzt als "Weitere Raeume"
- Aufgabenliste: Eintraege kompakter – Aktionsbuttons rechts inline statt separate Zeile unten
- CSS: .btn-outline fuer sekundaere Buttons ergaenzt

## 1.2.9

- Fix: FOUC (Aufblinken) beim Seitenwechsel beseitigt – kritisches Layout-CSS inline im `<head>` verhindert Flackern vor dem App.css-Laden
- Fix: `body { opacity: 0 }` inline + `opacity: 1; transition: 0.06s` in app.css sorgen fuer sauberes Einblenden ohne sichtbare Rohstruktur
- Admin-Bereich: Raum-Icons als visueller Picker mit Icon-Grid statt Dropdown
- Dashboard: Aufgaben-Zeilen kompakter mit `.dash-task`-Layout (Icon, Name, Badge, Erledigt-Button in einer Zeile)
- Neue CSS-Variable `--sep` fuer Listentrennlinien (rgba-basiert, garantierter Kontrast in Light und Dark Mode)

## 1.2.8

- Fix: Trennlinien zwischen Aufgaben, Räumen und Projektschritten jetzt in Dark und Light Mode sichtbar
- Neue CSS-Variable --sep (rgba-basiert) statt --border für Listentrennlinien – garantierter Kontrast auf jedem Hintergrund

## 1.2.7

- Dashboard: Aufgaben-Zeilen kompakter – Icon 36px, Name+Badge+Erledigt-Button in einer Zeile, kein separater Aktions-Block
- Dashboard: Klare Trenner zwischen Aufgaben und Räumen per border-bottom statt unsichtbarem 1px-Gap
- Dashboard: Räume nutzen jetzt saubere border-bottom-Trenner ohne list-card-Wrapper

## 1.2.6

- Admin: Raum-Icons jetzt als visueller Picker – kompaktes Karten-Grid mit allen Icon-Optionen zum Anklicken
- Admin: Vorschau-Bubble aktualisiert sich live beim Klick ohne Seitenreload

## 1.2.5

- Fix: Defektes HTML im Admin Panel behoben (Raum-Icons: `</section>` statt `</div>`, kein-Admins-Banner: `</div>` statt `</section>`)
- Aufräumen: Toter `_CSS`-Inline-Block (~230 Zeilen) aus render.py entfernt – `app.css` ist die einzige CSS-Quelle
- Light Mode: Hintergrund von kühlem Blaugrau auf warmes Mauve-Rosa angepasst (`#f4f0f2`)
- Light Mode: Ring-Chart-Hintergrundring jetzt klar sichtbar (`#e0d8dc` statt fast-weißem `#f0f2f5`)
- Light Mode: Cards mit stärkerem Schatten und etwas kräftigerer Border
- Light Mode: App-Titel im Header jetzt in `--primary-dark` statt `--text`

## 1.2.4

- Admins behalten beim Wechsel auf andere Personen den Personenumschalter im Header
- Neue Rückkehrpfade für Admins: eigene Ansicht, eigenes Profil und Person wechseln
- Aufgaben- und Projektaktionen behalten die aktive Personenansicht nach Speichern, Erledigen und Löschen bei
- Admin-Seite klarer gegliedert in Admin-Rechte, Raum-Icons, Benachrichtigungen und Personeneinstellungen
- Raum-Icon-Auswahl nutzt jetzt eigene Raum-Symbole statt Aufgaben-Icons; bestehende alte Icon-Zuweisungen bleiben sichtbar
- App-Version, Add-on-Version und README-Badge auf 1.2.4 aktualisiert

## 1.2.3

- Admin-Dashboard und Standardlisten zeigen wieder nur eigene Aufgaben und eigene Projektanteile
- Admins können Aufgaben in Raumansichten weiterhin nach Personen gruppiert sehen
- Admins können Projekte über "Nach Personen" gruppiert nach Zuständigkeit ansehen
- Eltern sehen standardmäßig eigene Aufgaben und in Raumansichten zusätzlich Aufgaben von Personen mit Rolle "Kind"
- Projekt-Detailansichten bleiben standardmäßig persönlich gefiltert; Admins können aus der Personenansicht heraus vollständig prüfen

## 1.2.2

- Projektschritte speichern jetzt eine eigene zugewiesene Person
- Änderungen der Person im Projektschritt werden direkt gespeichert
- Neue Projektschritte übernehmen standardmäßig die Projektperson
- Beim Abhaken wird die Schrittperson als erledigende Person verwendet
- Aufgaben-, Projekt- und Dashboard-Ansichten filtern für Nicht-Admins nach persönlicher Zuweisung

## 1.2.1

- Projekt-Detailansicht: Beim Abhaken eines Projektschritts wird die dem Projekt zugewiesene Person vorausgewählt
- Projekt-Detailansicht: Gespeicherte Projektperson bleibt auswählbar, auch wenn sie nicht aus der aktuellen HA-Personenliste kommt
- Projekt-Schritte: Aufgeräumtes Layout mit stabiler Aktionsgruppe für Person, Erledigt und Löschen
- Formular "Schritt hinzufügen": Klarere Button-Zeile für Hinzufügen und Zurück zu allen Projekten
- Health-Endpunkt und App-Version sind mit der Add-on-Version synchron

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
