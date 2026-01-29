#!/usr/bin/env python3
"""
Extrahiert ALLE Felder aus dem DSAusländer PDF vollständig.
Erstellt eine umfassende field_descriptions_extracted.json mit:
- Blattnummer (z.B. "031" für NodeShape, "031.01" für PropertyShape)
- Feldname
- Beschreibung (vollständig)
- Rechtliche Grundlagen
- Darstellungsform (inkl. URN für Codelisten)
- Vorgaben
- Hinweise zur Datenqualität
- Bestandteil der Gruppe (für PropertyShapes)
- Beinhaltet (für NodeShapes)
- Feldlänge, Feldtyp (Fest/Variabel), Häufigkeit
- Seite im PDF
"""

import pdfplumber
import re
import json
from pathlib import Path
from datetime import datetime

def clean_text(text):
    """Bereinigt Text von überflüssigen Whitespaces."""
    if not text:
        return ""
    # Ersetze mehrfache Leerzeichen/Zeilenumbrüche durch einzelne
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_blatt_nummer(text):
    """Extrahiert Blattnummer aus verschiedenen Formaten."""
    # PropertyShape: "011.03 Ort" am Anfang der Seite
    ps_match = re.search(r'(?:^|\n)\s*(\d{3}\.\d{2})\s+\w+', text, re.MULTILINE)
    if ps_match:
        return ps_match.group(1), 'propertyshape'
    
    # NodeShape: "004 - Grundpersonalien" MIT "Beinhaltet"
    # (nur die erste Seite eines NodeShapes hat "Beinhaltet")
    ns_match = re.search(r'^\s*(\d{3})\s*[-–]\s*\w+', text, re.MULTILINE)
    if ns_match and 'Beinhaltet' in text:
        blatt = ns_match.group(1)
        # Prüfe ob Blatt am Anfang ist (erste 300 Zeichen)
        if text.find(f'{blatt} -') < 300 or text.find(f'{blatt} –') < 300:
            return blatt, 'nodeshape'
    
    return None, None

def extract_propertyshape_metadata(page_text, blatt, page_num):
    """Extrahiert Metadaten für PropertyShape (XXX.YY Format)."""
    metadata = {
        'seite': page_num,
        'blatt': blatt,
        'typ': 'propertyshape',
        'feldname': None,
        'feldbezeichnung': None,
        'feldlaenge': None,
        'fest_variabel': None,
        'haeufigkeit': None,
        'beschreibung': None,
        'vorgaben': None,
        'rechtliche_grundlagen': None,
        'hinweise_datenqualitaet': None,
        'darstellungsform': None,
        'bestandteil_der_gruppe': None
    }
    
    # Feldname (direkt nach Blattnummer)
    feldname_pattern = rf'{re.escape(blatt)}\s+(\w+(?:\s+\w+)?)'
    feldname_match = re.search(feldname_pattern, page_text)
    if feldname_match:
        metadata['feldname'] = clean_text(feldname_match.group(1))
    
    # Feldbezeichnung (unter "Feldbezeichnung")
    feldbez_match = re.search(r'Feldbezeichnung\s+([^\n]+)', page_text)
    if feldbez_match:
        metadata['feldbezeichnung'] = clean_text(feldbez_match.group(1))
    
    # Feldlänge
    feldl_match = re.search(r'Feldlänge\s+(\d+)', page_text)
    if feldl_match:
        metadata['feldlaenge'] = feldl_match.group(1)
    
    # Fest/Variabel
    festvar_match = re.search(r'Fest/\s*variabel\s+(Fest|Variabel)', page_text, re.IGNORECASE)
    if festvar_match:
        metadata['fest_variabel'] = festvar_match.group(1)
    
    # Häufigkeit
    haeuf_match = re.search(r'Häufigkeit\s+([\d.]+)', page_text)
    if haeuf_match:
        metadata['haeufigkeit'] = haeuf_match.group(1)
    
    # Vorgaben
    vorg_match = re.search(r'Vorgaben\s+([^\n]+)', page_text)
    if vorg_match:
        metadata['vorgaben'] = clean_text(vorg_match.group(1))
    
    # Beschreibung des Feldinhalts
    besch_match = re.search(r'Beschreibung des Feldinhalts\s+(.*?)(?=Hinweise zur Datenqualität|Rechtliche Grundlagen|Darstellungsform|Bestandteil der Gruppe|$)', 
                            page_text, re.DOTALL)
    if besch_match:
        metadata['beschreibung'] = clean_text(besch_match.group(1))
    
    # Hinweise zur Datenqualität
    hinw_match = re.search(r'Hinweise zur Datenqualität\s+(.*?)(?=Rechtliche Grundlagen|Darstellungsform|Bestandteil der Gruppe|$)', 
                           page_text, re.DOTALL)
    if hinw_match:
        metadata['hinweise_datenqualitaet'] = clean_text(hinw_match.group(1))
    
    # Rechtliche Grundlagen
    rechtl_match = re.search(r'Rechtliche Grundlagen\s+(.*?)(?=Darstellungsform|Bestandteil der Gruppe|$)', 
                             page_text, re.DOTALL)
    if rechtl_match:
        metadata['rechtliche_grundlagen'] = clean_text(rechtl_match.group(1))
    
    # Darstellungsform
    darst_match = re.search(r'Darstellungsform\s+(.*?)(?=Bestandteil der Gruppe|$)', 
                            page_text, re.DOTALL)
    if darst_match:
        metadata['darstellungsform'] = clean_text(darst_match.group(1))
    
    # Bestandteil der Gruppe
    bestand_match = re.search(r'Bestandteil der Gruppe\s+(\d{3}\s*[-–]\s*[^\n]+)', page_text)
    if bestand_match:
        metadata['bestandteil_der_gruppe'] = clean_text(bestand_match.group(1))
    
    return metadata

def extract_nodeshape_metadata(page_text, blatt, page_num):
    """Extrahiert Metadaten für NodeShape (XXX Format)."""
    metadata = {
        'seite': page_num,
        'blatt': blatt,
        'typ': 'nodeshape',
        'feldname': None,
        'beschreibung': None,
        'rechtliche_grundlagen': None,
        'hinweise_datenqualitaet': None,
        'beinhaltet': None
    }
    
    # Feldname (nach "XXX -")
    feldname_pattern = rf'{re.escape(blatt)}\s*[-–]\s*([^\n]+)'
    feldname_match = re.search(feldname_pattern, page_text)
    if feldname_match:
        metadata['feldname'] = clean_text(feldname_match.group(1))
    
    # Beschreibung - alles zwischen Feldname und "Beinhaltet"
    if metadata['feldname']:
        # Finde Position nach Feldname
        start_pos = page_text.find(metadata['feldname'])
        if start_pos > -1:
            start_pos += len(metadata['feldname'])
            # Finde Ende (vor "Beinhaltet" oder "Rechtliche Grundlagen")
            end_markers = ['Beinhaltet', 'Rechtliche Grundlagen', 'Hinweise']
            end_pos = len(page_text)
            for marker in end_markers:
                marker_pos = page_text.find(marker, start_pos)
                if marker_pos > -1 and marker_pos < end_pos:
                    end_pos = marker_pos
            
            beschreibung = page_text[start_pos:end_pos]
            metadata['beschreibung'] = clean_text(beschreibung)
    
    # Beinhaltet (Liste der PropertyShapes)
    beinh_match = re.search(r'Beinhaltet\s*:?\s*(.*?)(?=Rechtliche Grundlagen|Hinweise|$)', 
                            page_text, re.DOTALL)
    if beinh_match:
        beinhaltet_text = beinh_match.group(1)
        # Extrahiere alle XXX.YY Nummern
        nummern = re.findall(r'\d{3}\.\d{2}', beinhaltet_text)
        if nummern:
            metadata['beinhaltet'] = sorted(list(set(nummern)))
    
    # Rechtliche Grundlagen
    rechtl_match = re.search(r'Rechtliche Grundlagen\s*:?\s*(.*?)(?=Hinweise|$)', 
                             page_text, re.DOTALL)
    if rechtl_match:
        metadata['rechtliche_grundlagen'] = clean_text(rechtl_match.group(1))
    
    # Hinweise zur Datenqualität
    hinw_match = re.search(r'Hinweise zur Datenqualität\s*:?\s*(.*?)$', 
                           page_text, re.DOTALL)
    if hinw_match:
        metadata['hinweise_datenqualitaet'] = clean_text(hinw_match.group(1))
    
    return metadata

def main():
    base_dir = Path(__file__).parent.parent
    pdf_path = base_dir / "doc" / "20250501_datensatz_v7.pdf"
    output_path = base_dir / "field_descriptions_complete.json"
    
    if not pdf_path.exists():
        print(f"❌ PDF nicht gefunden: {pdf_path}")
        return
    
    print("="*70)
    print("VOLLSTÄNDIGE PDF-EXTRAKTION")
    print("="*70)
    print(f"PDF: {pdf_path.name}")
    
    all_fields = {}
    nodeshapes = []
    propertyshapes = []
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"Seiten: {total_pages}")
        print("\n🔍 Extrahiere Felder...")
        
        for page_num, page in enumerate(pdf.pages, start=1):
            # Progress alle 25 Seiten
            if page_num % 25 == 0:
                print(f"   Fortschritt: {page_num}/{total_pages} Seiten " 
                      f"({len(nodeshapes)} NodeShapes, {len(propertyshapes)} PropertyShapes)")
            
            text = page.extract_text()
            
            if not text:
                continue
            
            # Bestimme Typ
            blatt, typ = extract_blatt_nummer(text)
            
            if not blatt:
                continue
            
            # Extrahiere basierend auf Typ
            try:
                if typ == 'propertyshape':
                    metadata = extract_propertyshape_metadata(text, blatt, page_num)
                    if metadata and metadata.get('feldname'):
                        all_fields[blatt] = metadata
                        propertyshapes.append(blatt)
                        if len(propertyshapes) % 10 == 0:
                            print(f"     → PropertyShape {blatt}: {metadata['feldname']}")
                elif typ == 'nodeshape':
                    metadata = extract_nodeshape_metadata(text, blatt, page_num)
                    if metadata and metadata.get('feldname'):
                        all_fields[blatt] = metadata
                        nodeshapes.append(blatt)
                        print(f"   ✓ NodeShape {blatt}: {metadata['feldname']}")
            except Exception as e:
                print(f"   ⚠️  Fehler Seite {page_num}, Blatt {blatt}: {str(e)[:40]}")
    
    # Speichern
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'extracted_at': datetime.now().isoformat(),
            'source': str(pdf_path),
            'total_nodeshapes': len(nodeshapes),
            'total_propertyshapes': len(propertyshapes),
            'nodeshapes': sorted(nodeshapes),
            'propertyshapes': sorted(propertyshapes),
            'fields': all_fields
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Gespeichert: {output_path.name}")
    print(f"\n📊 Statistik:")
    print(f"   NodeShapes: {len(nodeshapes)}")
    print(f"   PropertyShapes: {len(propertyshapes)}")
    print(f"   Gesamt: {len(all_fields)}")
    print("\n" + "="*70)
    print("✅ EXTRAKTION ABGESCHLOSSEN")
    print("="*70)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
