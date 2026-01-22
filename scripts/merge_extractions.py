#!/usr/bin/env python3
"""
Zusammenführung der NodeShapes und PropertyShapes zu einem kompletten Datensatz.
"""

import json
from pathlib import Path
from datetime import datetime

def merge_extractions():
    # Lade beide Extrakte
    with open('field_descriptions_complete.json', 'r', encoding='utf-8') as f:
        propertyshapes_data = json.load(f)
    
    with open('nodeshapes_extracted.json', 'r', encoding='utf-8') as f:
        nodeshapes_data = json.load(f)
    
    # Kombiniere
    all_fields = {}
    
    # PropertyShapes hinzufügen
    for blatt, data in propertyshapes_data['fields'].items():
        all_fields[blatt] = data
    
    # NodeShapes hinzufügen
    for blatt, data in nodeshapes_data['nodeshapes'].items():
        all_fields[blatt] = data
    
    # Gruppiere nach Typ
    nodeshapes = {k: v for k, v in all_fields.items() if v.get('typ') == 'nodeshape'}
    propertyshapes = {k: v for k, v in all_fields.items() if v.get('typ') == 'propertyshape'}
    
    # Erstelle finale Struktur
    final_data = {
        'extracted_at': datetime.now().isoformat(),
        'source': 'doc/20250501_datensatz_v7.pdf',
        'pdf_version': 7,
        'statistics': {
            'total_fields': len(all_fields),
            'nodeshapes': len(nodeshapes),
            'propertyshapes': len(propertyshapes)
        },
        'nodeshapes': sorted(nodeshapes.keys()),
        'propertyshapes': sorted(propertyshapes.keys()),
        'fields': all_fields
    }
    
    # Speichern
    output_path = Path('field_descriptions_complete_merged.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print("="*70)
    print("✅ VOLLSTÄNDIGE EXTRAKTION ABGESCHLOSSEN")
    print("="*70)
    print(f"NodeShapes:     {len(nodeshapes):3d}")
    print(f"PropertyShapes: {len(propertyshapes):3d}")
    print(f"GESAMT:         {len(all_fields):3d}")
    print()
    print(f"💾 Gespeichert in: {output_path}")
    print("="*70)
    
    # Beispiele
    print("\n📋 Beispiel NodeShape:")
    example_ns = nodeshapes[list(nodeshapes.keys())[0]]
    print(f"  Blatt: {example_ns['blatt']}")
    print(f"  Feldname: {example_ns['feldname']}")
    print(f"  Beinhaltet: {len(example_ns.get('beinhaltet', []))} PropertyShapes")
    
    print("\n📋 Beispiel PropertyShape:")
    example_ps = propertyshapes[list(propertyshapes.keys())[0]]
    print(f"  Blatt: {example_ps['blatt']}")
    print(f"  Feldname: {example_ps.get('feldname', 'N/A')}")
    if example_ps.get('feldlaenge'):
        print(f"  Feldlänge: {example_ps['feldlaenge']}")
    
    return final_data

if __name__ == "__main__":
    merge_extractions()
