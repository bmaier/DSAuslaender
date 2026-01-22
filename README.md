# DSAusländer Ontologie & SHACL Shapes

Ontologie und SHACL-Validierungsregeln für den Datensatz des Ausländerwesens (DSAusländer).

**Quelle:** Datensatzbeschreibung Version 7 (Stand 01.05.2025)  
**Stand:** 22. Januar 2026

---

## 📁 Projektstruktur

### Produktive Dateien (aktiv genutzt)

```
.
├── README.md                                    # Diese Datei
├── SHAPES_GENERATION_README.md                  # Dokumentation der SHACL-Generierung
├── PROJEKT_STRUKTUR.md                          # Detaillierte Projektbeschreibung
├── BESCHREIBUNGEN_WORKFLOW.md                   # Workflow-Dokumentation
│
├── dsauslaender-ontology.ttl                    # Haupt-Ontologie (OWL/RDFS)
├── dsauslaender-shapes.ttl                      # SHACL Shapes (generiert, 415 Felder)
├── field_descriptions_complete_merged.json      # Vollständige PDF-Extraktion
│
├── spec/
│   ├── 20250501_datensatz_v7.pdf               # Offizielle Datensatzbeschreibung
│   ├── 20250501_datensatz_v7_converted.md      # PDF → Markdown Konvertierung
│   └── field_specifications.json               # Feld-Spezifikationen
│
├── vocabularies/                                # SKOS Codelisten
│   ├── geschlecht.ttl
│   ├── staatsangehoerigkeit.ttl
│   ├── sensitivitaet.ttl
│   └── ...
│
└── scripts/                                     # Aktive Skripte
    ├── generate_shacl_shapes_from_pdf.py       # SHACL-Generierung (Hauptskript)
    ├── extract_all_fields_from_pdf.py          # PropertyShape-Extraktion
    ├── extract_nodeshapes_only.py              # NodeShape-Extraktion
    ├── merge_extractions.py                    # Zusammenführung der Extrakte
    └── check_extraction_quality.py             # Qualitätsprüfung
```

### Archiv (historisch)

```
archive/
├── old-shacl/                                   # Alte SHACL-Dateien (vor Neugenerierung)
│   └── dsauslaender-shapes.ttl
├── intermediate-extractions/                    # Zwischenergebnisse der Extraktion
│   ├── field_descriptions_complete.json
│   ├── nodeshapes_extracted.json
│   └── field_descriptions_extracted.json
├── old-csvs/                                    # Alte CSV-Exporte
│   ├── field_descriptions_extracted.csv
│   ├── field_descriptions_merged.csv
│   └── field_descriptions_template.csv
├── old-scripts/                                 # Alte/historische Skripte
│   ├── transform_generic_shapes_v2.py
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

### Extrahierte Daten
- **415 Felder** aus 482 PDF-Seiten
  - **60 NodeShapes** (Gruppen wie "Grundpersonalien", "Anschrift", etc.)
  - **355 PropertyShapes** (einzelne Felder wie "Familienname", "Geburtsdatum", etc.)

### Generierte SHACL-Datei
- **6.127 Zeilen** Turtle-Code
- **3.740 RDF-Tripel**
- **403 Shapes** (60 NodeShapes + 343 PropertyShapes)
- **217 KB** Dateigröße

### Datenqualität
- ✅ 100% PropertyShapes mit Beschreibung
- ✅ 100% PropertyShapes mit Vorgaben/Constraints
- ✅ 98% NodeShapes mit Beinhaltet-Listen
- ✅ 26% PropertyShapes mit Codelist-Referenzen (SKOS)

---

## 🎯 Design-Prinzipien

### 1. Trennung von Metadaten und Validierung

**Ontologie** (`dsauslaender-ontology.ttl`):
- Semantische Beschreibungen (rdfs:comment, rdfs:label)
- Property-Definitionen (owl:DatatypeProperty, owl:ObjectProperty)
- Klassenstruktur (owl:Class)
- Rechtliche Grundlagen

**SHACL** (`dsauslaender-shapes.ttl`):
- Validierungs-Constraints (sh:datatype, sh:maxLength, sh:pattern)
- Kardinalitäten (sh:minCount, sh:maxCount)
- Property-Shapes für Kontext
- Referenzen zur Ontologie (sh:path)

### 2. SKOS für Codelisten

Statt `sh:in` mit hardcodierten Werten:
```turtle
dsa:geschlechtPropertyShape
    dsa:codelist <urn:de:xauslaender:codelist:azr:geschlecht> ;
    sh:nodeKind sh:IRI ;
    sh:class skos:Concept .
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

Alle Constraints stammen aus dem offiziellen PDF:
- Feldlängen aus "Feldlänge"
- Datentypen aus "Darstellungsform"
- Kardinalitäten aus "Häufigkeit"
- Codelisten aus URN-Referenzen

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

**Version:** 1.0  
**Stand:** 22. Januar 2026  
**Basierend auf:** DSAusländer Datensatzbeschreibung Version 7 (01.05.2025)
