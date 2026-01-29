# Changelog - DSAusländer Ontologie

## Version 1.2.0 (29. Januar 2026)

### Hauptänderungen

#### ✓ XRepository-Integration abgeschlossen
- Alle SKOS-Vokabulare mit offiziellen XRepository-Standards verknüpft
- `dct:source` zeigt auf XRepository Details-Seiten (nicht Download-URLs)
- `base:xRepositoryURN` enthält korrekte URNs (keine URLs)
- `skos:exactMatch` verwendet korrekte Namespaces pro Standard

#### ✓ Standards korrigiert
| Vocabulary | Standard | URN Namespace | Status |
|------------|----------|---------------|--------|
| geschlecht.ttl | XInneres | `urn:xoev-de:xinneres:codeliste:geschlecht` | ✓ Korrigiert |
| asylentscheidung.ttl | XAusländer AZR | `urn:de:xauslaender:codelist:azr:asylstatus` | ✓ Korrigiert |
| aufenthaltstitel.ttl | XAusländer AZR | `urn:de:xauslaender:codelist:azr:niederlassungserlaubnis` | ✓ Korrigiert |
| familienstand.ttl | XAusländer | `urn:de:xauslaender:codelist:familienstand` | ✓ Validiert |
| staatsangehoerigkeit.ttl | DESTATIS | `urn:de:bund:destatis:bevoelkerungsstatistik:*` | ✓ Validiert |

#### ✓ SHACL-Shapes angereichert
- 400 PropertyShapes mit PDF-Metadaten angereichert (+2,131 Triples)
- Neue Annotation Properties: rechtlicheGrundlagen, hinweiseDatenqualitaet, darstellungsform, vorgaben, beinhaltet, blatt
- Redundante Properties entfernt: dsa:pdfPage, dsa:seite (-811 Triples)

#### ✓ Ontologie bereinigt
- aufenthaltszweck vollständig entfernt (nicht im PDF verwendet)
- 9 Annotation Properties hinzugefügt
- Finale Größe: 2,086 Triples

#### ✓ Validierung
- Alle TTL-Dateien mit `rapper` validiert
- Syntax-Fehler behoben (Leerzeichen in Konzept-IDs)
- Triple-Counts verifiziert

### Dateien

**Geändert:**
- dsauslaender-ontology.ttl (2,086 Triples)
- dsauslaender-shapes.ttl (5,371 Triples)
- vocabularies/geschlecht.ttl (64 Triples)
- vocabularies/asylentscheidung.ttl (178 Triples)
- vocabularies/aufenthaltstitel.ttl (127 Triples)
- vocabularies/familienstand.ttl (132 Triples)
- vocabularies/staatsangehoerigkeit.ttl (328 Triples)

**Entfernt:**
- vocabularies/aufenthaltszweck.ttl (nicht in PDF)

**Aufgeräumt:**
- 38 Backup-Dateien → backups/
- 4 Analyse-Skripte → ignored/old-scripts/
- Reports → ignored/analysis-reports/

### Migration Notes

**Breaking Changes:**
- `base:xRepositoryURN` ist jetzt echte URN statt URL
- geschlecht.ttl verwendet XInneres statt XAusländer Namespace
- aufenthaltszweck-Referenzen entfernt

**Empfohlene Aktionen:**
1. SPARQL-Queries auf neue URN-Formate anpassen
2. Geschlecht-Referenzen auf XInneres-Namespace aktualisieren
3. aufenthaltszweck-Referenzen entfernen oder ersetzen

---

## Version 1.0.0-beta (22. Januar 2026)

### Initiale Version
- 415 Felder aus PDF extrahiert
- SHACL Shapes generiert (3,740 Triples)
- Erste SKOS-Vokabulare erstellt
- Ontologie mit Properties und Classes
