# DSAusländer SHACL Shapes - Generierung und Design-Entscheidungen

## Überblick

Dieses Dokument beschreibt den Ansatz zur Generierung der SHACL-Shapes-Datei `dsauslaender-shapes.ttl` aus dem offiziellen DSAusländer Datensatzbeschreibung PDF (Version 7, Stand 01.05.2025).

**Datum:** 22. Januar 2026  
**Quelle:** `spec/20250501_datensatz_v7.pdf` (482 Seiten)  
**Extrahierte Felder:** 415 (60 NodeShapes + 355 PropertyShapes)

---

## Design-Entscheidungen

### 1. Trennung von Metadaten und SHACL-Validierung

**Entscheidung:** Metadaten (Beschreibungen, rechtliche Grundlagen, etc.) werden NICHT in der SHACL-Datei gespeichert, sondern referenzieren die Ontologie.

**Begründung:**
- **Separation of Concerns:** SHACL ist für Validierung zuständig, Ontologie für semantische Beschreibung
- **Wartbarkeit:** Änderungen an Beschreibungen erfordern keine SHACL-Änderungen
- **Machine-Readability:** Tools können Validierung und Semantik unabhängig verarbeiten
- **Best Practice:** Entspricht W3C-Empfehlungen (SHACL + RDFS/OWL Ontology)

**Implementierung:**
```turtle
# ❌ NICHT: Metadaten in SHACL
dsa:familiennamePersonPropertyShape
    rdfs:label "Familienname" ;
    rdfs:comment "Der Familienname bezeichnet..." ;
    dct:description "Vollständige Beschreibung..." .

# ✅ STATTDESSEN: Referenz zur Ontology
dsa:familiennamePersonPropertyShape
    sh:path dsa:familienname ;  # Referenz zur Ontologie-Property
    sh:datatype xsd:string ;
    sh:maxLength 90 .
```

### 2. SKOS für Codelisten

**Entscheidung:** Codelisten werden als SKOS ConceptSchemes modelliert, nicht als sh:in Listen.

**Begründung:**
- **Erweiterbarkeit:** Neue Code-Werte können hinzugefügt werden ohne SHACL-Änderungen
- **Semantische Reichhaltigkeit:** SKOS bietet skos:prefLabel, skos:definition, skos:broader, etc.
- **Integration:** Codelisten können in anderen Systemen wiederverwendet werden
- **PDF-Vorgabe:** PDF verwendet URN-Referenzen (z.B. `urn:de:xauslaender:codelist:azr:geschlecht`)

**Implementierung:**
```turtle
# ❌ NICHT: Hardcoded sh:in
dsa:geschlechtPersonPropertyShape
    sh:in ( "M" "W" "D" "X" ) .

# ✅ STATTDESSEN: SKOS-Referenz
dsa:geschlechtPersonPropertyShape
    sh:path dsa:geschlecht ;
    sh:nodeKind sh:IRI ;
    sh:class skos:Concept ;
    dsa:codelist <urn:de:xauslaender:codelist:azr:geschlecht> .
```

### 3. Kontextspezifische PropertyShapes

**Entscheidung:** Jede Property erhält einen kontextspezifischen Namen (z.B. `ereignisdatumAsylstatusPropertyShape`).

**Begründung:**
- **Präzision:** Ereignisdatum in Asylstatus hat andere Constraints als in Abschiebung
- **Wartbarkeit:** Änderungen an einem Kontext beeinflussen nicht andere
- **Nachvollziehbarkeit:** Name zeigt direkt, wo die Property verwendet wird
- **PDF-Struktur:** PDF definiert Properties mehrfach in verschiedenen NodeShapes

**Implementierung:**
```turtle
# Ereignisdatum erscheint 32x im PDF mit unterschiedlichen Blattnummern
dsa:ereignisdatumAsylstatusPropertyShape      # In NodeShape "Asylstatus" (028)
dsa:ereignisdatumAbschiebungPropertyShape     # In NodeShape "Abschiebung" (043)
dsa:ereignisdatumMeldestatusPropertyShape     # In NodeShape "Meldestatus" (024)
# ... etc.
```

### 4. Keine Annahmen - Nur PDF-Daten

**Entscheidung:** Alle Daten stammen aus dem PDF. Keine Erfindungen, keine Annahmen.

**Begründung:**
- **Verlässlichkeit:** PDF ist die offizielle Spezifikation
- **Nachweisbarkeit:** Jede Constraint kann zum PDF zurückverfolgt werden
- **Compliance:** Erfüllt rechtliche und organisatorische Vorgaben
- **Qualität:** Verhindert Fehler durch Spekulation

**Implementierung:**
- Jedes Feld hat Referenz zur PDF-Seite (`dsa:pdfPage`)
- Feldlängen, Datentypen, Patterns stammen aus "Darstellungsform"
- Cardinalitäten stammen aus "Häufigkeit"
- Labels stammen aus "Feldbezeichnung"

### 5. NodeShape-Struktur

**Entscheidung:** NodeShapes repräsentieren Gruppen und referenzieren ihre PropertyShapes.

**Begründung:**
- **Modularität:** PropertyShapes können in mehreren NodeShapes verwendet werden
- **Validierung:** sh:property ermöglicht Validierung der gesamten Gruppe
- **Navigation:** Klare Struktur von Gruppe → Felder
- **PDF-Entsprechung:** PDF definiert "Beinhaltet"-Listen für jede Gruppe

**Implementierung:**
```turtle
dsa:PersonNodeShape
    a sh:NodeShape ;
    sh:targetClass dsa:Person ;
    rdfs:label "Grundpersonalien" ;
    dsa:blattnummer "004" ;
    sh:property dsa:familiennamePersonPropertyShape ;
    sh:property dsa:vornamePersonPropertyShape ;
    sh:property dsa:geburtsdatumPersonPropertyShape ;
    # ... weitere 10 Properties
    .
```

---

## Dateistruktur

### Generierte Dateien

```
dsauslaender-shapes.ttl             # Haupt-SHACL-Datei (generiert)
├── Prefix-Deklarationen
├── Dokumentations-Kommentare
├── NodeShapes (60)
│   └── sh:property → PropertyShapes
└── PropertyShapes (355)
    ├── sh:path → Ontologie-Property
    ├── sh:datatype / sh:class
    ├── sh:minLength / sh:maxLength
    ├── sh:pattern
    └── dsa:codelist → SKOS ConceptScheme

dsauslaender-ontology.ttl           # Ontologie (manuell gepflegt)
├── owl:Class Definitionen
├── owl:ObjectProperty
├── owl:DatatypeProperty
└── rdfs:label, rdfs:comment

vocabularies/                        # SKOS Codelisten (manuell)
├── geschlecht.ttl
├── staatsangehoerigkeit.ttl
├── sensitivitaet.ttl
└── ...
```

### Quelldaten

```
field_descriptions_complete_merged.json   # Vollständige Extraktion (415 Felder)
├── nodeshapes: [...]                     # 60 NodeShapes mit Beinhaltet-Listen
├── propertyshapes: [...]                 # 355 PropertyShapes
└── fields: { "004": {...}, "004.01": {...}, ... }

spec/20250501_datensatz_v7.pdf             # Offizielle Quelle (482 Seiten)
```

---

## Generierungsprozess

### Phase 1: PDF-Extraktion ✅ ABGESCHLOSSEN

```bash
# 1. PropertyShapes extrahieren
python3 scripts/extract_all_fields_from_pdf.py
# Ergebnis: 355 PropertyShapes in field_descriptions_complete.json

# 2. NodeShapes extrahieren
python3 scripts/extract_nodeshapes_only.py
# Ergebnis: 60 NodeShapes in nodeshapes_extracted.json

# 3. Zusammenführen
python3 scripts/merge_extractions.py
# Ergebnis: 415 Felder in field_descriptions_complete_merged.json

# 4. Qualitätsprüfung
python3 scripts/check_extraction_quality.py
# Ergebnis: 100% Beschreibungen, 98% Beinhaltet-Listen
```

### Phase 2: SHACL-Generierung (IN ARBEIT)

```bash
# Generiere dsauslaender-shapes.ttl aus JSON
python3 scripts/generate_shacl_shapes_from_pdf.py

# Validiere Syntax
rapper -i turtle -c dsauslaender-shapes.ttl

# Prüfe gegen Ontologie
python3 scripts/validate_shapes_against_ontology.py
```

---

## Mapping: PDF → SHACL

### PropertyShape-Felder

| PDF-Feld | SHACL-Property | Beispiel |
|----------|----------------|----------|
| Feldbezeichnung | rdfs:label | "Familienname" |
| Feldlänge | sh:maxLength | 90 |
| Fest/Variabel | sh:minLength | 90 (bei "fest") |
| Häufigkeit | sh:minCount / sh:maxCount | "1" → min/max 1 |
| Darstellungsform | sh:pattern / sh:datatype | "[0-9]{6}" → sh:pattern |
| Darstellungsform (URN) | dsa:codelist | urn:...→ SKOS |
| Vorgaben | sh:pattern (erweitert) | "allgemeinerName" |
| Bestandteil der Gruppe | (implizit) | Via NodeShape sh:property |

### NodeShape-Felder

| PDF-Feld | SHACL-Property | Beispiel |
|----------|----------------|----------|
| Blattnummer | dsa:blattnummer | "004" |
| Feldname/Gruppe | rdfs:label | "Grundpersonalien" |
| Beinhaltet | sh:property | Liste von PropertyShapes |
| Beschreibung | rdfs:comment | (aus Ontologie) |

---

## Ausnahmen und Sonderfälle

### 1. PropertyShapes ohne NodeShape

**Blattnummern:** 001, 002, 003, 008, 009, 016, 018, 019, 021, 027, 065

**Behandlung:** Diese werden als eigenständige PropertyShapes generiert, da sie laut PDF keine Gruppe bilden.

```turtle
# 001 = Aktenführende Behörde (keine Gruppe)
dsa:aktenfuehrendeBehördePropertyShape
    a sh:PropertyShape ;
    sh:path dsa:aktenfuehrendeBehörde ;
    sh:datatype xsd:string ;
    sh:pattern "[0-9]{6}" ;
    dsa:blattnummer "001" .
```

### 2. Mehrfach vorkommende Feldnamen

**Problem:** "Ereignisdatum" kommt 32x in verschiedenen NodeShapes vor.

**Lösung:** Kontextspezifische Namen mit Blattnummer-Suffix.

```turtle
dsa:ereignisdatum024PersonPropertyShape  # In Blatt 024
dsa:ereignisdatum028PersonPropertyShape  # In Blatt 028
# ... etc.
```

### 3. Codelisten ohne URN

**Problem:** Manche Felder haben Vorgaben ohne URN (z.B. "allgemeinerName").

**Lösung:** Pattern-basierte Validierung statt SKOS.

```turtle
# Hat URN → SKOS
dsa:geschlechtPersonPropertyShape
    dsa:codelist <urn:de:xauslaender:codelist:azr:geschlecht> .

# Kein URN → Pattern
dsa:familiennamePersonPropertyShape
    sh:pattern "^[\\p{L}\\s'-]+$" .  # Unicode-Buchstaben, Leerzeichen, Bindestrich
```

---

## Validierung

### Syntaktische Validierung

```bash
# Turtle-Syntax prüfen
rapper -i turtle -c dsauslaender-shapes.ttl

# SHACL-Syntax prüfen (mit rdflib)
python3 scripts/validate_shacl_syntax.py
```

### Semantische Validierung

```bash
# Prüfe dass alle sh:path Properties in Ontologie existieren
python3 scripts/check_ontology_references.py

# Prüfe dass alle Codelisten existieren
python3 scripts/check_vocabulary_references.py

# Prüfe dass alle NodeShape-PropertyShape-Referenzen gültig sind
python3 scripts/check_shape_references.py
```

### Vollständigkeitsprüfung

```bash
# Vergleiche mit PDF: Alle 415 Felder vorhanden?
python3 scripts/check_completeness.py
```

---

## Wartung und Updates

### Bei PDF-Update

1. Neue PDF in `spec/` ablegen
2. Extraktion erneut ausführen (Phase 1)
3. Diff zwischen altem und neuem JSON prüfen
4. SHACL neu generieren (Phase 2)
5. Validierungen durchführen
6. Git Commit mit PDF-Version im Commit-Message

### Bei Ontologie-Änderung

1. `dsauslaender-ontology.ttl` manuell ändern
2. Validierung durchführen: `scripts/validate_shapes_against_ontology.py`
3. Bei Bedarf SHACL-Shapes anpassen

### Bei Vocabulary-Änderung

1. Entsprechende Datei in `vocabularies/` ändern
2. Validierung: `scripts/check_vocabulary_references.py`
3. SHACL-Shapes referenzieren Vocabularies nur, keine Änderung nötig

---

## Technische Details

### Verwendete Standards

- **SHACL:** W3C SHACL Shapes Constraint Language
- **RDF:** Resource Description Framework (Turtle-Syntax)
- **RDFS:** RDF Schema für Labels und Kommentare
- **OWL:** Web Ontology Language für Ontologie
- **SKOS:** Simple Knowledge Organization System für Codelisten
- **XSD:** XML Schema Datatypes für sh:datatype

### Tool-Stack

- **Python 3.13:** Extraktion und Generierung
- **pdfplumber:** PDF-Text-Extraktion
- **rdflib:** RDF-Manipulation und Validierung
- **rapper:** Turtle-Syntax-Validierung (optional)

### Performance

- **Extraktion:** ~5-10 Minuten für 482 Seiten
- **Generierung:** ~30 Sekunden für 415 Shapes
- **Validierung:** ~5 Sekunden für syntaktische Prüfung

---

## Referenzen

### Spezifikationen

- [SHACL W3C Recommendation](https://www.w3.org/TR/shacl/)
- [RDF 1.1 Turtle](https://www.w3.org/TR/turtle/)
- [SKOS Reference](https://www.w3.org/TR/skos-reference/)

### Projekt-Dateien

- `dsauslaender-ontology.ttl` - Ontologie mit Property-Definitionen
- `dsauslaender-shapes.ttl` - Alte SHACL-Datei (vor Neugenerierung)
- `dsauslaender-shapes.ttl` - Neue SHACL-Datei (generiert)
- `field_descriptions_complete_merged.json` - Extrahierte PDF-Daten

### Skripte

- `scripts/extract_all_fields_from_pdf.py` - PropertyShape-Extraktion
- `scripts/extract_nodeshapes_only.py` - NodeShape-Extraktion
- `scripts/merge_extractions.py` - Zusammenführung
- `scripts/generate_shacl_shapes_from_pdf.py` - SHACL-Generierung
- `scripts/check_extraction_quality.py` - Qualitätsprüfung

---

## Lizenz und Urheberrecht
## Lizenz

Der Quellcode und die generierten SHACL-Shapes stehen unter der [Apache License, Version 2.0](https://www.apache.org/licenses/LICENSE-2.0).

```
Copyright 2026 Bundesamt für Migration und Flüchtlinge (BAMF)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

**Hinweis:**  
Die Datensatzbeschreibung ist Eigentum des Bundesamts für Migration und Flüchtlinge (BAMF).  
Diese Shapes-Datei ist eine technische Implementierung der offiziellen Spezifikation, stellt jedoch selbst keine offizielle Version des Bundesamts für Migration und Flüchtlinge (BAMF) dar.

**Stand:** 22. Januar 2026  
**Version:** 1.0 (basierend auf PDF Version 7, Stand 01.05.2025)
