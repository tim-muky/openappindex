# Anbieter-Fragebogen v1 (Entwurf, 2026-09-17)

Kanonische Fassung: `sample/questionnaire_v1.json`. Diese Seite ist die lesbare Form und wird vor dem ersten Versand auf der Methodenseite veröffentlicht (GAL-579). Solange dieser Entwurf nicht dort steht, wird der Fragebogen an niemanden geschickt.

## Regel: wer gefragt wird

Jede App im Index ist berechtigt, keine wird ausgewählt. Jede App, die der wöchentliche Vergleich (`/de/aenderungen/`) als neu im Index erkennt, erhält den Fragebogen einmal, automatisch. Anbieterinnen und Anbieter jeder gelisteten App können ihn jederzeit selbst beantworten. Höchstens eine Erinnerung. Keine Interviews, keine redaktionelle Nachbearbeitung.

## Regel: wie veröffentlicht wird

- Auf der Seite der App in einem eigenen Block: **„Angabe des Anbieters (selbst gemeldet, von openAPPindex nicht geprüft)“**, mit Datum der Antwort.
- Neben den gemessenen Werten, nie mit ihnen vermischt. Weichen Angabe und Messung voneinander ab, stehen beide da.
- **Keine Antwort ist eine Tatsache:** „Fragebogen gesendet am …, keine Antwort bis …“ steht auf der Seite. Antwortquote pro Kategorie wird als datierte Zahl veröffentlicht.
- Die Antworten werden Felder im offenen Datensatz (CC BY 4.0): `developer_stated_*`, dazu `questionnaire_version`, `sent_at`, `answered_at`, `withdrawn_at`.
- Freitext wird wörtlich und gekürzt auf 300 Zeichen veröffentlicht. Wir redigieren, fassen zusammen und zitieren nicht.

## Die zehn Fragen (identisch für jede App, versioniert)

1. Welche juristische Person steht hinter der App, und in welchem Land ist sie registriert?
2. Welches Preismodell hat die App? (gratis / Einmalkauf / Abo / gemischt)
3. Für jeden im Store ausgewiesenen In-App-Kauf: Welcher Abrechnungszeitraum gilt? (wöchentlich / monatlich / vierteljährlich / jährlich / einmalig / Verbrauchsgut / anderes) — **Diese Angabe veröffentlicht Apple nicht; deshalb rechnet der Index nichts auf ein Jahr hoch. Sie wird als Anbieterangabe veröffentlicht und auch danach nicht von uns hochgerechnet.**
4. Was kann die App ohne Bezahlung? (voller Umfang / eingeschränkt / Test mit automatischer Umwandlung / Test ohne automatische Umwandlung / nichts)
5. Enthält die App Werbung? (keine / nur eigene Produkte / Dritt-SDKs, mit Namen)
6. Können Nutzerinnen und Nutzer ihre eigenen Daten in einem offenen Format exportieren? (ja/nein, Formate)
7. Kann das Konto in der App selbst gelöscht werden? (ja/nein)
8. Ist der Quellcode verfügbar? (geschlossen / einsehbar / Open Source, Lizenz, Repository-URL)
9. Über welchen Kanal ist der Support erreichbar, und welche Antwortzeit sagen Sie zu?
10. Was sollten Leserinnen und Leser darüber wissen, wie diese App gepflegt wird? (höchstens 300 Zeichen, wörtlich veröffentlicht, keine Links, keine Personennamen)

Nicht gefragt wird: nach einer Selbsteinschätzung der Qualität, nach Download- oder Umsatzzahlen, nach einzelnen Nutzerinnen oder Rezensionen. Links sind nur in Frage 8 zulässig.

## Versand

- Kontaktweg: nur, was der Store selbst veröffentlicht (Anbieter- bzw. Support-URL der App).
- Eine Nachricht, reiner Text, mit der veröffentlichten Regel, dem Hinweis auf die CC-BY-Veröffentlichung und der Möglichkeit abzulehnen. Ablehnungen werden sofort umgesetzt.
- Absender: eine eigene Subdomain mit eigenem SPF/DKIM, nie das Hauptpostfach von openappindex.org.
- Rechtsgrundlage für die Verarbeitung der Kontaktdaten: berechtigtes Interesse (Art. 6 Abs. 1 lit. f DSGVO), Datenschutzhinweis in der Nachricht und im Formular. Eine echte Recherche-Anfrage ist keine Werbung im Sinne von § 7 UWG; sie bleibt trotzdem bei einer Nachricht.

## Eingang

- GitHub-Issue-Vorlage **und** E-Mail-Adresse, weil nicht jeder Anbieter ein GitHub-Konto hat.
- Prüfung nur auf Schema-Gültigkeit, nicht auf Inhalt → JSON-Datensatz → Pull Request → Build.

## Einwilligungstext

> Ihre Antworten werden als „Angabe des Anbieters (selbst gemeldet, von openAPPindex nicht geprüft)“ mit Datum auf der Seite Ihrer App und im offenen Datensatz (CC BY 4.0) veröffentlicht. Sie können Ihre Angaben jederzeit aktualisieren oder zurückziehen; ein Rückzug wird mit Datum vermerkt. Bitte nennen Sie keine Personen im Freitext.
