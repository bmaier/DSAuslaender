#!/usr/bin/env python3
"""Qualitätsprüfung der Extraktion."""

import json

with open('field_descriptions_complete_merged.json') as f:
    data = json.load(f)

print("="*70)
print("QUALITÄTSPRÜFUNG DER EXTRAKTION")
print("="*70)

fields = data['fields']

# PropertyShapes
propertyshapes = [f for f in fields.values() if f.get('typ') == 'propertyshape']
ps_with_beschreibung = sum(1 for f in propertyshapes if f.get('beschreibung'))
ps_with_darstellungsform = sum(1 for f in propertyshapes if f.get('darstellungsform'))
ps_with_vorgaben = sum(1 for f in propertyshapes if f.get('vorgaben'))

# NodeShapes
nodeshapes = [f for f in fields.values() if f.get('typ') == 'nodeshape']
ns_with_beinhaltet = sum(1 for f in nodeshapes if f.get('beinhaltet'))

print(f"\nPropertyShapes ({len(propertyshapes)}):")
print(f"  Mit Beschreibung:      {ps_with_beschreibung:3d} ({ps_with_beschreibung/len(propertyshapes)*100:.0f}%)")
print(f"  Mit Darstellungsform:  {ps_with_darstellungsform:3d} ({ps_with_darstellungsform/len(propertyshapes)*100:.0f}%)")
print(f"  Mit Vorgaben:          {ps_with_vorgaben:3d} ({ps_with_vorgaben/len(propertyshapes)*100:.0f}%)")

print(f"\nNodeShapes ({len(nodeshapes)}):")
print(f"  Mit Beinhaltet:        {ns_with_beinhaltet:3d} ({ns_with_beinhaltet/len(nodeshapes)*100:.0f}%)")

# Beispiele
print("\n" + "="*70)
print("BEISPIEL: NodeShape 004")
print("="*70)
ns_004 = fields['004']
print(f"Feldname: {ns_004['feldname']}")
print(f"Beinhaltet: {', '.join(ns_004['beinhaltet'][:10])}...")

print("\n" + "="*70)
print("BEISPIEL: PropertyShape 004.01")
print("="*70)
ps_004_01 = fields['004.01']
for key, value in ps_004_01.items():
    if value and key not in ['seite', 'blatt', 'typ']:
        print(f"{key}: {str(value)[:80]}")
