#!/usr/bin/env python3
"""
Generiert dsauslaender-shapes-new.ttl aus den extrahierten PDF-Daten.

DESIGN-ENTSCHEIDUNGEN:
====================

1. TRENNUNG VON METADATEN UND SHACL
   - Metadaten (Beschreibungen, rechtliche Grundlagen) → Ontologie
   - Validierungs-Constraints (sh:datatype, sh:maxLength) → SHACL
   - Begründung: Separation of Concerns, bessere Wartbarkeit

2. SKOS FÜR CODELISTEN
   - Codelisten werden als SKOS ConceptSchemes referenziert
   - Statt sh:in → dsa:codelist <urn:...>
   - Begründung: Erweiterbarkeit, semantische Reichhaltigkeit

3. KONTEXTSPEZIFISCHE PROPERTYSHAPES
   - Jede Property bekommt kontextspezifischen Namen
   - z.B. ereignisdatumAsylstatusPropertyShape
   - Begründung: Verschiedene Contexts = verschiedene Constraints

4. KEINE ANNAHMEN
   - Alle Daten stammen aus dem PDF
   - Bei fehlenden Daten: Frage stellen, nicht erfinden
   - Begründung: Verlässlichkeit und Compliance

STRUKTUR DER GENERIERTEN DATEI:
==============================

@prefix dsa: <http://example.org/dsauslaender#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
...

# === NODESHAPES (Gruppen) ===
dsa:PersonNodeShape ...
dsa:AnschriftNodeShape ...

# === PROPERTYSHAPES (Felder) ===
dsa:familiennamePersonPropertyShape ...
dsa:vornamePersonPropertyShape ...

DATENFLUSS:
==========

field_descriptions_complete_merged.json
  → 415 Felder (60 NodeShapes + 355 PropertyShapes)
  → SHACL-Generierung
  → dsauslaender-shapes-new.ttl

"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# ============================================================================
# KONFIGURATION
# ============================================================================

INPUT_JSON = Path("field_descriptions_complete_merged.json")
OUTPUT_TTL = Path("dsauslaender-shapes-new.ttl")
ONTOLOGY_FILE = Path("dsauslaender-ontology.ttl")

# Prefix-Definitionen
PREFIXES = {
    'dsa': 'http://example.org/dsauslaender#',
    'sh': 'http://www.w3.org/ns/shacl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'dct': 'http://purl.org/dc/terms/',
    'sens': 'http://example.org/dsauslaender/vocabulary/sensitivitaet#',
}

# PropertyShapes ohne NodeShape (laut PDF)
STANDALONE_PROPERTIES = ['001', '002', '003', '008', '009', '016', '018', '019', '021', '027', '065']


# ============================================================================
# HILFSFUNKTIONEN
# ============================================================================

def sanitize_name(name: str) -> str:
    """
    Konvertiert Feldname in gültigen Turtle-Identifier.
    
    DESIGN: CamelCase für bessere Lesbarkeit
    Beispiel: "Aktenführende Behörde" → "aktenfuehrendeBehörde"
    """
    if not name:
        return "unknown"
    
    # Entferne Sonderzeichen, ersetze Umlaute
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'
    }
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Entferne alle nicht-alphanumerischen Zeichen außer Leerzeichen
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    
    # CamelCase
    parts = name.split()
    if not parts:
        return "unknown"
    
    result = parts[0].lower()
    for part in parts[1:]:
        result += part.capitalize()
    
    return result


def map_datatype(darstellungsform: str, feldlaenge) -> str:
    """
    Mappt Darstellungsform aus PDF auf XSD-Datentyp.
    
    DESIGN: Konservativ - bei Unsicherheit xsd:string verwenden
    """
    if not darstellungsform:
        return 'xsd:string'
    
    df_lower = darstellungsform.lower()
    
    # Zahlenformate
    if re.search(r'\[0-9\]', darstellungsform):
        try:
            laenge = int(feldlaenge) if feldlaenge else 999
            if laenge <= 10:
                return 'xsd:integer'
        except (ValueError, TypeError):
            pass
        return 'xsd:string'  # Große Zahlen als String (z.B. Behördenkennzeichen)
    
    # Datumformate
    if 'datum' in df_lower or re.search(r'dd\.mm\.yyyy', darstellungsform):
        return 'xsd:date'
    
    # Boolean
    if 'ja/nein' in df_lower or 'boolean' in df_lower:
        return 'xsd:boolean'
    
    # Standard: String
    return 'xsd:string'


def extract_pattern(darstellungsform: str) -> str:
    """
    Extrahiert Regex-Pattern aus Darstellungsform.
    
    DESIGN: Nur wenn eindeutig Pattern erkennbar
    Beispiel: "[0-9]{6}" → "^[0-9]{6}$"
    """
    if not darstellungsform:
        return None
    
    # Suche nach Regex-Pattern in eckigen Klammern
    pattern_match = re.search(r'\[([^\]]+)\](\{[\d,]+\})?', darstellungsform)
    if pattern_match:
        base = pattern_match.group(1)
        quantifier = pattern_match.group(2) if pattern_match.group(2) else ''
        return f"^{base}{quantifier}$"
    
    return None


def extract_cardinality(haeufigkeit: str) -> tuple:
    """
    Extrahiert sh:minCount und sh:maxCount aus Häufigkeit.
    
    DESIGN: 
    - "1" → minCount 1, maxCount 1
    - "0..1" → minCount 0, maxCount 1
    - "1..*" → minCount 1, keine maxCount
    """
    if not haeufigkeit:
        return (None, None)
    
    h = haeufigkeit.strip()
    
    # Genau einmal
    if h == '1':
        return (1, 1)
    
    # Optional
    if h in ['0..1', '0 bis 1']:
        return (0, 1)
    
    # Mindestens einmal
    if h in ['1..*', '1 bis *', '1..*']:
        return (1, None)
    
    # Optional, mehrfach
    if h in ['0..*', '0 bis *']:
        return (0, None)
    
    # Versuche Bereichsextraktion
    range_match = re.match(r'(\d+)\.\.(\d+|\*)', h)
    if range_match:
        min_val = int(range_match.group(1))
        max_val = None if range_match.group(2) == '*' else int(range_match.group(2))
        return (min_val, max_val)
    
    return (None, None)


def is_codelist_reference(darstellungsform: str) -> str:
    """
    Prüft ob Darstellungsform eine Codelist-URN enthält.
    
    DESIGN: URN → SKOS-Referenz statt sh:in
    Beispiel: "urn:de:xauslaender:codelist:azr:geschlecht"
    """
    if not darstellungsform:
        return None
    
    urn_match = re.search(r'urn:de:xauslaender:codelist:[^\s,;]+', darstellungsform)
    if urn_match:
        return urn_match.group(0)
    
    return None


# ============================================================================
# HAUPTGENERIERUNG
# ============================================================================

def generate_header() -> List[str]:
    """Generiert Datei-Header mit Prefixes und Dokumentation."""
    lines = []
    
    # Prefixes
    lines.append("# ============================================================================")
    lines.append("# DSAusländer SHACL Shapes - Automatisch generiert")
    lines.append("# ============================================================================")
    lines.append("#")
    lines.append(f"# Generiert am: {datetime.now().isoformat()}")
    lines.append(f"# Quelle: doc/20250501_datensatz_v7.pdf (Version 7)")
    lines.append("# Extrahierte Felder: 415 (60 NodeShapes + 355 PropertyShapes)")
    lines.append("#")
    lines.append("# DESIGN-ENTSCHEIDUNGEN:")
    lines.append("# - Metadaten in Ontologie, Constraints in SHACL")
    lines.append("# - SKOS für Codelisten (statt sh:in)")
    lines.append("# - Kontextspezifische PropertyShape-Namen")
    lines.append("# - Keine Annahmen - nur PDF-Daten")
    lines.append("#")
    lines.append("# Siehe SHAPES_GENERATION_README.md für Details")
    lines.append("# ============================================================================")
    lines.append("")
    
    for prefix, uri in PREFIXES.items():
        lines.append(f"@prefix {prefix}: <{uri}> .")
    
    lines.append("")
    lines.append("# ============================================================================")
    lines.append("# NODESHAPES (Gruppen)")
    lines.append("# ============================================================================")
    lines.append("# NodeShapes repräsentieren Gruppen aus dem PDF.")
    lines.append("# Jede Gruppe enthält mehrere PropertyShapes (via sh:property).")
    lines.append("# ============================================================================")
    lines.append("")
    
    return lines


def generate_nodeshape(blatt: str, data: Dict[str, Any], all_fields: Dict) -> List[str]:
    """
    Generiert einen NodeShape aus den extrahierten Daten.
    
    STRUKTUR:
    dsa:PersonNodeShape
        a sh:NodeShape ;
        sh:targetClass dsa:Person ;
        rdfs:label "Grundpersonalien" ;
        dsa:blattnummer "004" ;
        dsa:pdfPage 48 ;
        sh:property dsa:familiennamePersonPropertyShape ;
        sh:property dsa:vornamePersonPropertyShape ;
        ...
    """
    lines = []
    
    feldname = data.get('feldname', f"Gruppe{blatt}")
    shape_name = sanitize_name(feldname) + "NodeShape"
    class_name = sanitize_name(feldname)
    
    lines.append(f"# Gruppe {blatt}: {feldname}")
    lines.append(f"# Beinhaltet {len(data.get('beinhaltet', []))} PropertyShapes")
    lines.append(f"# PDF-Seite: {data.get('seite', 'N/A')}")
    lines.append(f"dsa:{shape_name}")
    lines.append(f"    a sh:NodeShape ;")
    lines.append(f"    sh:targetClass dsa:{class_name} ;")
    lines.append(f'    rdfs:label "{feldname}" ;')
    lines.append(f'    dsa:blattnummer "{blatt}" ;')
    if data.get('seite'):
        lines.append(f"    dsa:pdfPage {data['seite']} ;")
    
    # PropertyShapes referenzieren
    beinhaltet = data.get('beinhaltet', [])
    if beinhaltet:
        for i, prop_blatt in enumerate(beinhaltet):
            # Finde PropertyShape-Daten
            prop_data = all_fields.get(prop_blatt, {})
            prop_feldname = prop_data.get('feldname', prop_blatt)
            
            # Generiere PropertyShape-Namen
            prop_shape_name = sanitize_name(prop_feldname) + class_name + "PropertyShape"
            
            if i == len(beinhaltet) - 1:
                lines.append(f"    sh:property dsa:{prop_shape_name} .")
            else:
                lines.append(f"    sh:property dsa:{prop_shape_name} ;")
    else:
        lines[-1] = lines[-1].rstrip(' ;') + " ."
    
    lines.append("")
    return lines


def generate_propertyshape(blatt: str, data: Dict[str, Any], context_name: str = None) -> List[str]:
    """
    Generiert einen PropertyShape aus den extrahierten Daten.
    
    STRUKTUR:
    dsa:familiennamePersonPropertyShape
        a sh:PropertyShape ;
        sh:path dsa:familienname ;
        rdfs:label "Familienname" ;
        dsa:blattnummer "004.01" ;
        dsa:pdfPage 49 ;
        sh:datatype xsd:string ;
        sh:maxLength 90 ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        dsa:bestandteilDerGruppe "004 - Grundpersonalien" .
    """
    lines = []
    
    feldname = data.get('feldname', f"Feld{blatt}")
    feldbezeichnung = data.get('feldbezeichnung', feldname)
    
    # PropertyShape-Name: feldname + Context
    if context_name:
        shape_name = sanitize_name(feldname) + context_name + "PropertyShape"
    else:
        shape_name = sanitize_name(feldname) + "PropertyShape"
    
    # Property-Name für sh:path
    property_name = sanitize_name(feldname)
    
    lines.append(f"# {blatt} - {feldbezeichnung}")
    lines.append(f"# PDF-Seite: {data.get('seite', 'N/A')}")
    
    # Beschreibung als Kommentar (nicht in RDF, da in Ontologie)
    if data.get('beschreibung'):
        lines.append(f"# Beschreibung: {data['beschreibung'][:80]}...")
    
    lines.append(f"dsa:{shape_name}")
    lines.append(f"    a sh:PropertyShape ;")
    lines.append(f"    sh:path dsa:{property_name} ;")
    lines.append(f'    rdfs:label "{feldbezeichnung}" ;')
    lines.append(f'    dsa:blattnummer "{blatt}" ;')
    
    if data.get('seite'):
        lines.append(f"    dsa:pdfPage {data['seite']} ;")
    
    # Datatype oder Codelist
    darstellungsform = data.get('darstellungsform', '')
    codelist_urn = is_codelist_reference(darstellungsform)
    
    if codelist_urn:
        # DESIGN: SKOS-Referenz statt sh:in
        lines.append(f"    sh:nodeKind sh:IRI ;")
        lines.append(f"    sh:class skos:Concept ;")
        lines.append(f"    dsa:codelist <{codelist_urn}> ;")
    else:
        # Normaler Datentyp
        datatype = map_datatype(darstellungsform, data.get('feldlaenge'))
        lines.append(f"    sh:datatype {datatype} ;")
        
        # Feldlänge
        if data.get('feldlaenge'):
            lines.append(f"    sh:maxLength {data['feldlaenge']} ;")
            
            # Feste Länge?
            fest_variabel = data.get('fest_variabel')
            if fest_variabel and fest_variabel.lower() == 'fest':
                lines.append(f"    sh:minLength {data['feldlaenge']} ;")
        
        # Pattern
        pattern = extract_pattern(darstellungsform)
        if pattern:
            # Escape für Turtle
            pattern_escaped = pattern.replace('\\', '\\\\')
            lines.append(f'    sh:pattern "{pattern_escaped}" ;')
    
    # Kardinalität
    min_count, max_count = extract_cardinality(data.get('haeufigkeit'))
    if min_count is not None:
        lines.append(f"    sh:minCount {min_count} ;")
    if max_count is not None:
        lines.append(f"    sh:maxCount {max_count} ;")
    
    # Bestandteil der Gruppe
    if data.get('bestandteil_der_gruppe'):
        gruppe = data['bestandteil_der_gruppe']
        lines.append(f'    dsa:bestandteilDerGruppe "{gruppe}" .')
    else:
        # Entferne letztes Semikolon
        lines[-1] = lines[-1].rstrip(' ;') + " ."
    
    lines.append("")
    return lines


def generate_shapes():
    """Hauptfunktion zur Generierung der SHACL-Shapes-Datei."""
    
    print("="*70)
    print("SHACL-SHAPES GENERIERUNG")
    print("="*70)
    
    # Lade Daten
    print(f"\n📖 Lade {INPUT_JSON}...")
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fields = data['fields']
    nodeshapes = [k for k in data['nodeshapes']]
    propertyshapes = [k for k in data['propertyshapes']]
    
    print(f"   {len(nodeshapes)} NodeShapes")
    print(f"   {len(propertyshapes)} PropertyShapes")
    
    # Generiere TTL
    print(f"\n🔨 Generiere {OUTPUT_TTL}...")
    
    lines = []
    
    # Header
    lines.extend(generate_header())
    
    # NodeShapes
    for blatt in sorted(nodeshapes):
        node_data = fields[blatt]
        lines.extend(generate_nodeshape(blatt, node_data, fields))
    
    # PropertyShapes-Sektion
    lines.append("# ============================================================================")
    lines.append("# PROPERTYSHAPES (Einzelne Felder)")
    lines.append("# ============================================================================")
    lines.append("# PropertyShapes definieren Constraints für Properties.")
    lines.append("# Kontextspezifische Namen (z.B. ereignisdatumAsylstatus) ermöglichen")
    lines.append("# unterschiedliche Constraints je nach Verwendungskontext.")
    lines.append("# ============================================================================")
    lines.append("")
    
    # PropertyShapes - gruppiert nach NodeShape
    processed = set()
    
    for blatt in sorted(nodeshapes):
        node_data = fields[blatt]
        context_name = sanitize_name(node_data.get('feldname', blatt))
        
        beinhaltet = node_data.get('beinhaltet', [])
        if beinhaltet:
            lines.append(f"# --- PropertyShapes für {node_data.get('feldname')} (Blatt {blatt}) ---")
            lines.append("")
            
            for prop_blatt in sorted(beinhaltet):
                if prop_blatt in processed:
                    continue
                
                prop_data = fields.get(prop_blatt, {})
                lines.extend(generate_propertyshape(prop_blatt, prop_data, context_name))
                processed.add(prop_blatt)
    
    # Standalone PropertyShapes (ohne NodeShape)
    lines.append("# ============================================================================")
    lines.append("# STANDALONE PROPERTYSHAPES (ohne Gruppe)")
    lines.append("# ============================================================================")
    lines.append("# Diese Felder bilden laut PDF keine Gruppe:")
    lines.append(f"# {', '.join(STANDALONE_PROPERTIES)}")
    lines.append("# ============================================================================")
    lines.append("")
    
    for blatt in sorted(propertyshapes):
        if blatt not in processed and blatt in STANDALONE_PROPERTIES:
            prop_data = fields.get(blatt, {})
            lines.extend(generate_propertyshape(blatt, prop_data, None))
            processed.add(blatt)
    
    # Speichere
    with open(OUTPUT_TTL, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n✅ Generierung abgeschlossen!")
    print(f"   Generierte Zeilen: {len(lines)}")
    print(f"   Datei: {OUTPUT_TTL}")
    
    # Statistiken
    nodeshape_count = len([l for l in lines if 'NodeShape' in l and 'a sh:NodeShape' in l])
    propertyshape_count = len([l for l in lines if 'PropertyShape' in l and 'a sh:PropertyShape' in l])
    
    print(f"\n📊 Statistik:")
    print(f"   NodeShapes:     {nodeshape_count}")
    print(f"   PropertyShapes: {propertyshape_count}")
    print(f"   Gesamt:         {nodeshape_count + propertyshape_count}")
    
    print("\n" + "="*70)
    print("NÄCHSTE SCHRITTE:")
    print("="*70)
    print("1. Syntaxprüfung: rapper -i turtle -c dsauslaender-shapes-new.ttl")
    print("2. Ontologie-Check: python3 scripts/validate_shapes_against_ontology.py")
    print("3. Vocabulary-Check: python3 scripts/check_vocabulary_references.py")
    print("="*70)


if __name__ == "__main__":
    generate_shapes()
