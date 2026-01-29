# DSAusländer Ontologie & SHACL Shapes

> **⚠️ ZWISCHENSTAND - WORK IN PROGRESS**  
> Version 1.2 - Nicht abgeschlossener Entwicklungsstand. Vollständige Validierung steht noch aus.

## ⚠️ Status und offene Punkte

**Dieser Stand ist nicht produktionsreif!** Folgende Aspekte sind noch offen bzw. in Diskussion:

### Offene Designentscheidungen
- ❓ **SKOS-Abbildung**: Die genaue Abbildung von Codelisten mit SKOS ist noch zu diskutieren
- ❓ **Ortsangaben**: Modellierung von Ortsreferenzen (GeoNames, Wikidata?) noch ungeklärt
- ❓ **Persistente Identifier**: Strategie für stabile URIs muss definiert werden (Hash-basiert? UUID? Sequential?)
- ❓ **Namespace-Strategie**: Finaler Namespace für Produktivbetrieb noch nicht festgelegt

### Noch ausstehend
- ⏳ **Validierung**: Vollständige SHACL-Validierung gegen Beispieldaten steht noch aus
- ⏳ **Integration-Tests**: Tests gegen XRepository-Standards noch nicht durchgeführt
- ⏳ **Peer-Review**: Fachliche Prüfung der Ontologie durch Domänenexperten ausstehend

---

## Über dieses Projekt

Dieses Projekt stellt eine maschinenlesbare Repräsentation des Datensatzes des Ausländerwesens (DSAusländer) bereit. Es umfasst:

- **OWL/RDFS Ontologie** für die semantische Beschreibung der Datenstruktur (2,086 Triples)
- **SHACL Shapes** für die automatisierte Validierung von Datensätzen (5,371 Triples)
- **SKOS Vokabulare** für standardisierte Codelisten mit XRepository-Integration
- **Vollständige PDF-Metadaten** in allen PropertyShapes (rechtliche Grundlagen, Datenqualität, etc.)

Die Implementierung basiert auf der vollständigen Extraktion aller 415 Felder aus der offiziellen Datensatzbeschreibung und ermöglicht die strukturierte Validierung und Integration von DSAusländer-Daten in Linked Data Systeme.

**Quelle:** Datensatzbeschreibung Version 7 (Stand 01.05.2025)  
**Stand:** 29. Januar 2026  
**Version:** 1.2.0

### ✓ XRepository-Integration und Standards

**Verwendete Standards:**
- **XInneres** (Geschlecht): `urn:xoev-de:xinneres:codeliste:geschlecht`
- **XAusländer** (Asyl, Aufenthalt, Familienstand): `urn:de:xauslaender:codelist:*`
- **DESTATIS** (Staatsangehörigkeit): `urn:de:bund:destatis:bevoelkerungsstatistik:*`

Alle SKOS-Vokabulare sind mit den offiziellen XRepository-Codelisten über `dct:source` und `skos:exactMatch` verknüpft. Die URNs entsprechen exakt den im PDF spezifizierten Standards (Feld "Darstellungsform" bei `vorgaben="code"`).

**Validierung:** Alle Turtle-Dateien sind mit `rapper` validiert und syntaktisch korrekt.

---

## 📁 Projektstruktur

### Produktive Dateien

```
.
├── README.md                                    # Projektübersicht
├── SHAPES_GENERATION_README.md                  # SHACL-Generierung Dokumentation
│
├── dsauslaender-ontology.ttl                    # Haupt-Ontologie (2,086 Triples)
├── dsauslaender-shapes.ttl                      # SHACL Shapes (5,371 Triples, 415 Felder)
├── field_descriptions_complete_merged.json      # Vollständige PDF-Extraktion (415 Felder)
│
├── vocabularies/                                # SKOS Codelisten mit XRepository-Links
│   ├── geschlecht.ttl                          # XInneres Standard (64 Triples)
│   ├── asylentscheidung.ttl                    # XAusländer AZR (178 Triples)
│   ├── aufenthaltstitel.ttl                    # XAusländer AZR (127 Triples)
│   ├── familienstand.ttl                       # XAusländer (132 Triples)
│   ├── staatsangehoerigkeit.ttl                # DESTATIS (328 Triples)
│   └── base.ttl                                # Basis-Vokabular
│
├── spec/
│   └── 20250501_datensatz_v7.pdf               # Offizielle Datensatzbeschreibung
│
└── scripts/                                     # Produktive Skripte
    ├── enrich_shapes_with_pdf_metadata_v2.py   # Metadaten-Enrichment
    ├── validate_vocabulary_urns.py             # URN-Validierung
    └── ...
```

### Nicht versionierte Verzeichnisse (.gitignore)

- `archive/` - Historische Dateien und alte Versionen
- `backups/` - Automatische Backups (38 TTL-Dateien)
- `ignored/` - Temporäre Analyse-Skripte und Reports
│   ├── add_pdf_descriptions.py
│   └── ... (weitere)
├── backups/                                     # Ontologie-Backups
│   ├── before-enrichment.ttl
│   └── ... (weitere)
└── generated-files/                             # Alte generierte Dateien
```

---

## 🚀 Schnellstart

### 1. SHACL Shapes neu generieren

```bash
# Aus PDF extrahieren und Shapes generieren (komplett)
python3 scripts/extract_all_fields_from_pdf.py
python3 scripts/extract_nodeshapes_only.py
python3 scripts/merge_extractions.py
python3 scripts/generate_shacl_shapes_from_pdf.py
```

### 2. Syntax validieren

```bash
# Mit rdflib (Python)
python3 -c "from rdflib import Graph; g = Graph(); g.parse('dsauslaender-shapes.ttl', format='turtle'); print(f'✅ {len(g)} Tripel')"

# Mit rapper (optional, falls installiert)
rapper -i turtle -c dsauslaender-shapes.ttl
```

### 3. Qualität prüfen

```bash
python3 scripts/check_extraction_quality.py
```

---

## 📊 Statistiken

### Kern-Dateien
| Datei | Triples | Zeilen | Status |
|-------|---------|--------|--------|
| **dsauslaender-ontology.ttl** | 2,086 | 2,788 | ✓ Validiert |
| **dsauslaender-shapes.ttl** | 5,371 | 7,388 | ✓ Validiert |
| **vocabularies/geschlecht.ttl** | 64 | 98 | ✓ XInneres |
| **vocabularies/asylentscheidung.ttl** | 178 | 222 | ✓ XAusländer AZR |
| **vocabularies/aufenthaltstitel.ttl** | 127 | 162 | ✓ XAusländer AZR |
| **vocabularies/familienstand.ttl** | 132 | 175 | ✓ XAusländer |
| **vocabularies/staatsangehoerigkeit.ttl** | 328 | 388 | ✓ DESTATIS |

### Extrahierte Daten
- **415 Felder** vollständig aus PDF extrahiert (15 Metadaten-Eigenschaften pro Feld)
- **60 NodeShapes** (Gruppen wie "Grundpersonalien", "Anschrift", etc.)
- **400 PropertyShapes** mit PDF-Metadaten angereichert (rechtliche Grundlagen, Datenqualität, etc.)

### Datenqualität
- ✅ 100% PropertyShapes mit PDF-Metadaten (rechtlicheGrundlagen, hinweiseDatenqualitaet, etc.)
- ✅ 100% PropertyShapes mit Validierungs-Constraints
- ✅ 100% SKOS-Vokabulare mit XRepository-Links (`dct:source`, `skos:exactMatch`)
- ✅ Alle Turtle-Dateien mit `rapper` validiert

---

## 🎯 Design-Prinzipien und getroffene Entscheidungen

### 0. Grundlegende Architektur-Entscheidung

**Problem**: Das DSAusländer PDF macht keine klare Trennung zwischen semantischen Definitionen (Ontologie) und Validierungsregeln (Constraints).

**Unsere Lösung**: Strikte Trennung in zwei Dateien:

**Ontologie** (`dsauslaender-ontology.ttl`):
- Semantische Beschreibungen (rdfs:comment, rdfs:label)
- Property-Definitionen (owl:DatatypeProperty, owl:ObjectProperty)
- Klassenstruktur (owl:Class)
- Domäne/Range-Definitionen
- Rechtliche Grundlagen als Annotationen

**SHACL** (`dsauslaender-shapes.ttl`):
- Validierungs-Constraints (sh:datatype, sh:maxLength, sh:pattern)
- Kardinalitäten (sh:minCount, sh:maxCount)
- PropertyShapes und NodeShapes
- Referenzen zur Ontologie via sh:path

**Begründung**: 
- Ontologie beschreibt was existiert (TBox)
- SHACL validiert konkrete Daten (ABox)
- Ermöglicht unterschiedliche Validierungsprofile
- Wiederverwendbarkeit der Ontologie ohne Constraints

### 1. Ausschließliche Verwendung von PropertyShapes und NodeShapes

**Entscheidung**: Keine Verwendung von `sh:NodeKind`, `sh:node` oder anderen SHACL-Konstrukten außer PropertyShapes und NodeShapes.

**Begründung**:
- PropertyShapes validieren einzelne Properties (Datenfelder)
- NodeShapes gruppieren PropertyShapes logisch (entspricht PDF-Kapiteln)
- Klare Zuordnung: 1 PDF-Feld = 1 PropertyShape
- Wartbarkeit: Jedes Feld ist eigenständig modifizierbar
- Nachvollziehbarkeit: Direkte Rückverfolgung zu PDF-Zeilen möglich

**Beispiel**:
```turtle
# NodeShape für logische Gruppierung
dsa:grundpersonalienNodeShape
    a sh:NodeShape ;
    sh:targetClass dsa:AuslaendischePerson ;
    sh:property dsa:vornamenPropertyShape ;
    sh:property dsa:familiennamePropertyShape .

# PropertyShape für konkretes Feld
dsa:vornamenPropertyShape
    a sh:PropertyShape ;
    sh:path dsa:vornamen ;
    sh:datatype xsd:string ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    dsa:blatt "001" .
```

### 2. Kardinalitäts-Mapping

**Entscheidung**: Konsistente Abbildung von PDF-Häufigkeit auf SHACL-Constraints:

| PDF: `dsa:haeufigkeit` | SHACL Constraints | Bedeutung |
|------------------------|-------------------|-----------|
| `"1"` | `sh:minCount 1`, `sh:maxCount 1` | Genau einmal (Pflichtfeld) |
| `"n"` | `sh:minCount 0`, kein maxCount | Beliebig oft (optional, wiederholbar) |

**Begründung**:
- `haeufigkeit "1"` = erforderlich (required) → minCount muss 1 sein
- `haeufigkeit "n"` = optional und wiederholbar → minCount 0, kein maxCount
- Konsistenz über alle 415 Felder hinweg
- Direkte Rückverfolgbarkeit zum PDF

**Wichtig**: Frühere Inkonsistenzen (minCount 0 bei haeufigkeit "1") wurden korrigiert.

### 3. Trennung von Metadaten und Validierung

**SHACL** (`dsauslaender-shapes.ttl`):
- Validierungs-Constraints (sh:datatype, sh:maxLength, sh:pattern)
- Kardinalitäten (sh:minCount, sh:maxCount)
- Property-Shapes für Kontext
- Referenzen zur Ontologie (sh:path)

### 4. SKOS für Codelisten mit XRepository-Integration

### 3. Property-Benennung

**Entscheidung**: Sprechende, kontextbezogene Namen statt generischer Bezeichnungen.

**Beispiel Ereignisdatum**:
- ❌ NICHT: `ereignisdatumPropertyShape` (zu generisch)
- ✅ SONDERN:
  - `ereignisdatumAsylstatusPropertyShape`
  - `ereignisdatumAbschiebungPropertyShape`
  - `ereignisdatumMeldestatusPropertyShape`

**Begründung**:
- Unterschiedliche Kontexte können unterschiedliche Constraints haben
- Eindeutige Zuordnung zu PDF-Abschnitten
- Erleichtert Wartung und Verständnis

### 4. Metadaten-Properties für PDF-Rückverfolgbarkeit

**Entscheidung**: Jede PropertyShape enthält:
- `dsa:blatt` - Blatt-/Feldnummer im PDF (z.B. "001", "002a")
- `dsa:feldnummer` - Redundante Kopie für Konsistenz
- `dsa:haeufigkeit` - "1" oder "n" (Pflicht/Optional)
- Weitere PDF-Metadaten wo relevant (rechtlicheGrundlagen, hinweiseDatenqualitaet)

**Begründung**:
- Direkte Rückverfolgung zu PDF-Spezifikation
- Nachvollziehbarkeit bei Updates
- Ermöglicht automatische Diff-Reports bei PDF-Änderungen

**Stand 29.01.2026**: Property `dsa:blatt` wird verwendet (vorher `dsa:blattnummer`), keine Internationalisierung (@de).

### 5. SKOS für Codelisten mit XRepository-Integration

Alle Codelisten sind als SKOS-Vokabulare implementiert und mit XRepository verknüpft:

```turtle
# ConceptScheme mit XRepository-Link
<https://bamf.bund.de/vocab/geschlecht> a skos:ConceptScheme ;
    base:xRepositoryURN "urn:xoev-de:xinneres:codeliste:geschlecht"^^xsd:anyURI ;
    dct:source <https://www.xrepository.de/details/urn:xoev-de:xinneres:codeliste:geschlecht> .

# Concept mit exactMatch zum Standard
:Maennlich a skos:Concept ;
    skos:notation "m" ;
    skos:exactMatch <urn:xoev-de:xinneres:codeliste:geschlecht:m> .
```

**SHACL-Validation**:
```turtle
sh:property [
    sh:path dsa:geschlecht ;
    sh:nodeKind sh:IRI ;
    sh:class skos:Concept .
] .
```

Vorteile:
- Erweiterbar ohne SHACL-Änderungen
- Semantisch reichhaltig (skos:prefLabel, skos:definition)
- Wiederverwendbar in anderen Systemen

### 3. Kontextspezifische PropertyShapes

Statt einem generischen `ereignisdatumPropertyShape`:
```turtle
dsa:ereignisdatumAsylstatusPropertyShape       # In Asylstatus-Kontext
dsa:ereignisdatumAbschiebungPropertyShape      # In Abschiebungs-Kontext
dsa:ereignisdatumMeldestatusPropertyShape      # In Meldestatus-Kontext
```

Begründung: Unterschiedliche Kontexte können unterschiedliche Constraints haben.

### 4. Keine Annahmen - Nur PDF-Daten
- XRepository-Konformität (urn:xoev-de:*, urn:de:bund:destatis:*)
- Internationale Standards werden respektiert

### 6. Keine Annahmen - Nur PDF-Daten

**Prinzip**: Alle Constraints stammen ausschließlich aus dem offiziellen PDF.

Alle Constraints stammen aus dem offiziellen PDF:
- Feldlängen aus "Feldlänge"
- **Feldlängen**: Aus Spalte "Feldlänge" im PDF
- **Datentypen**: Aus Spalte "Darstellungsform" abgeleitet
  - "JJJJMMTT" → xsd:date
  - "AN" → xsd:string
  - "code" → sh:IRI mit SKOS-Concept
- **Kardinalitäten**: Aus Spalte "Häufigkeit"
  - "1" → minCount 1, maxCount 1
  - "n" → minCount 0, kein maxCount
- **Codelisten**: Aus URN-Referenzen in "Darstellungsform"
- Codelisten aus URN-Referenzen

**Keine Eigeninterpretation**: Fehlende Informationen im PDF führen zu fehlenden Constraints.

### 7. Entfernte Properties (Stand 29.01.2026)

**Gelöscht**: 
- `dsa:pdfPage` - War redundant zu blatt
- `dsa:seite` - Ersetzt durch blatt
- Sprachmarkierungen `@de` - Nicht erforderlich, da einsprachiges System

**Umbenannt**:
- `dsa:blattnummer` → `dsa:blatt` (kürzere, klarere Bezeichnung)

---

## 📚 Dokumentation

- **[SHAPES_GENERATION_README.md](SHAPES_GENERATION_README.md)** - Vollständige Dokumentation der SHACL-Generierung
  - Design-Entscheidungen im Detail
  - Mapping PDF → SHACL
  - Wartungs- und Update-Prozesse
  
- **[PROJEKT_STRUKTUR.md](PROJEKT_STRUKTUR.md)** - Detaillierte Projektbeschreibung

- **[BESCHREIBUNGEN_WORKFLOW.md](BESCHREIBUNGEN_WORKFLOW.md)** - Workflow-Dokumentation

---

## 🔄 Workflow: PDF-Update

Bei einer neuen PDF-Version:

```bash
# 1. Neue PDF in spec/ ablegen
cp neue_version.pdf spec/

# 2. Vollständige Extraktion
python3 scripts/extract_all_fields_from_pdf.py
python3 scripts/extract_nodeshapes_only.py
python3 scripts/merge_extractions.py

# 3. Diff prüfen
diff field_descriptions_complete_merged.json archive/intermediate-extractions/field_descriptions_complete.json

# 4. SHACL neu generieren
python3 scripts/generate_shacl_shapes_from_pdf.py

# 5. Validieren
python3 scripts/check_extraction_quality.py
python3 -c "from rdflib import Graph; g = Graph(); g.parse('dsauslaender-shapes.ttl', format='turtle'); print('✅ OK')"

# 6. Alte Version archivieren
mv dsauslaender-shapes.ttl archive/old-shacl/dsauslaender-shapes-v7.ttl
mv field_descriptions_complete_merged.json archive/intermediate-extractions/

# 7. Git Commit
git add -A
git commit -m "Update zu PDF Version X (Stand DD.MM.YYYY)"
```

---

## 🛠️ Technologie-Stack

- **Python 3.13+** - Extraktion und Generierung
- **pdfplumber** - PDF-Text-Extraktion
- **rdflib** - RDF-Manipulation und Validierung
- **SHACL** - W3C SHACL Shapes Constraint Language
- **Turtle** - RDF-Serialisierung
- **SKOS** - Simple Knowledge Organization System
- **OWL/RDFS** - Ontologie-Beschreibung

---

## 📝 Lizenz und Urheberrecht

Die Datensatzbeschreibung ist Eigentum des Bundesamts für Migration und Flüchtlinge (BAMF).  
Diese Implementierung ist eine technische Umsetzung der offiziellen Spezifikation.

---

## 📞 Kontakt und Support

Bei Fragen zur Struktur oder Generierung:
- Siehe [SHAPES_GENERATION_README.md](SHAPES_GENERATION_README.md) für technische Details
- Prüfe `archive/` für historische Versionen
- Nutze die Skripte in `scripts/` für Regenerierung

**Version:** 1.2 (Work in Progress)  
**Stand:** 29. Januar 2026  
**Basierend auf:** DSAusländer Datensatzbeschreibung Version 7 (01.05.2025)  
**Status:** ⚠️ Nicht produktionsreif - Validierung und Review ausstehend

---

## 📋 Änderungshistorie (29.01.2026)

### Durchgeführte Korrekturen
- ✅ Property-Umbenennung: `blattnummer` → `blatt`
- ✅ Entfernung redundanter Properties: `pdfPage`, `seite`, `feldnummer` (aus Ontologie)
- ✅ Entfernung von `@de` Sprachmarkierungen
- ✅ **Kardinalitäts-Fix**: 
  - Alle `haeufigkeit "1"` haben jetzt korrekt `sh:minCount 1` und `sh:maxCount 1`
  - Alle `haeufigkeit "n"` haben jetzt korrekt `sh:minCount 0` ohne maxCount
  - Vorher: Inkonsistenzen, teilweise minCount 0 bei Pflichtfeldern

### Validierung
- ✅ dsauslaender-shapes.ttl: 3,686 Triples (rapper validiert)
- ✅ dsauslaender-ontology.ttl: 2,113 Triples (rapper validiert)
- ✅ 8 PropertyShapes mit korrekten Kardinalitäts-Constraints

