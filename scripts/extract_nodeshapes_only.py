#!/usr/bin/env python3
"""
Extrahiert NUR NodeShapes aus dem PDF.
NodeShapes sind in einem separaten Abschnitt und haben Format:
- "Gruppe XXX" oder nur "XXX Feldname" als Überschrift
- Enthalten "Beinhaltet:" mit Liste der PropertyShapes
"""

import pdfplumber
import re
import json
from pathlib import Path

def extract_nodeshapes():
    pdf_path = Path("doc/20250501_datensatz_v7.pdf")
    nodeshapes = {}
    
    print("🔍 Suche NodeShapes im PDF...")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in range(1, len(pdf.pages) + 1):
            text = pdf.pages[page_num-1].extract_text()
            
            # Suche nach "Gruppe XXX" Pattern
            gruppe_match = re.search(r'Gruppe\s+(\d{3})', text)
            
            # Oder suche nach standalone "XXX Feldname" mit "Beinhaltet"
            standalone_match = re.search(r'^(\d{3})\s+([A-Z][^\n]{5,60})$', text, re.MULTILINE)
            
            if (gruppe_match or standalone_match) and 'Beinhaltet' in text:
                # Finde Blattnummer
                if gruppe_match:
                    blatt = gruppe_match.group(1)
                elif standalone_match:
                    blatt = standalone_match.group(1)
                else:
                    continue
                
                # Prüfe ob bereits vorhanden
                if blatt in nodeshapes:
                    continue
                
                # Extrahiere Feldname
                feldname = None
                if standalone_match:
                    feldname = standalone_match.group(2).strip()
                else:
                    # Suche in Zeilen nach Gruppe
                    lines = text.split('\n')
                    for i, line in enumerate(lines):
                        if f'Gruppe {blatt}' in line:
                            # Feldname oft in nächster Zeile oder gleicher Zeile
                            if i+1 < len(lines):
                                feldname = lines[i+1].strip()
                            break
                
                # Extrahiere "Beinhaltet"
                beinhaltet = []
                beinh_match = re.search(r'Beinhaltet\s*:?\s*(.*?)(?=Rechtliche Grundlagen|Hinweise|$)', 
                                        text, re.DOTALL)
                if beinh_match:
                    beinhaltet_text = beinh_match.group(1)
                    nummern = re.findall(r'\d{3}\.\d{2}', beinhaltet_text)
                    beinhaltet = sorted(list(set(nummern)))
                
                nodeshapes[blatt] = {
                    'blatt': blatt,
                    'typ': 'nodeshape',
                    'feldname': feldname,
                    'seite': page_num,
                    'beinhaltet': beinhaltet
                }
                
                print(f"✓ NodeShape {blatt}: {feldname} (Seite {page_num}, {len(beinhaltet)} PropertyShapes)")
    
    print(f"\n📊 Gesamt: {len(nodeshapes)} NodeShapes gefunden")
    return nodeshapes

if __name__ == "__main__":
    nodeshapes = extract_nodeshapes()
    
    output_path = Path("nodeshapes_extracted.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'total': len(nodeshapes),
            'nodeshapes': nodeshapes
        }, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Gespeichert in: {output_path}")
