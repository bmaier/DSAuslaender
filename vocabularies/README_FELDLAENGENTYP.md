# Feldlängentyp-Vokabular

## Übersicht

Das Feldlängentyp-Vokabular klassifiziert, ob ein Datenfeld eine **feste** oder **variable** Länge hat. Dies ist wichtig für die Validierung und effiziente Speicherung der Daten.

## Vokabular-URI

**Namespace:** `http://bamf.de/vocabulary/feldlaengentyp#`  
**Prefix:** `feldtyp:`

## Konzepte

### 1. Fest (Fixed Length)

**URI:** `feldtyp:Fest`  
**Notation:** `F`  
**Präfix-Label:** "fest" (de), "fixed" (en)

**Definition:** Das Feld hat eine feste, nicht variable Länge. Die Anzahl der Zeichen ist exakt vorgegeben und muss eingehalten werden.

**Beispiele:**
- Behördenkennzeichen (6 Zeichen)
- Postleitzahl (5 Zeichen)
- Geschlecht (1 Zeichen)
- ISO-Datum (10 Zeichen: YYYY-MM-DD)

**SHACL-Ausdruck:**
```turtle
:BeispielShape a sh:PropertyShape ;
    ex:feldlaengenTyp feldtyp:Fest ;
    sh:minLength 6 ;
    sh:maxLength 6 ;
    sh:pattern "^[0-9]{6}$" .
```

**Hinweis:** Feste Feldlängen werden in SHACL durch `sh:minLength = sh:maxLength` ausgedrückt.

### 2. Variabel (Variable Length)

**URI:** `feldtyp:Variabel`  
**Notation:** `V`  
**Präfix-Label:** "variabel" (de), "variable" (en)

**Definition:** Das Feld hat eine variable Länge bis zu einem definierten Maximum. Die tatsächliche Länge kann von 0 bis zum Maximalwert variieren.

**Beispiele:**
- Familienname (max. 100 Zeichen)
- Straße (max. 100 Zeichen)
- Geschäftszeichen (max. 50 Zeichen)

**SHACL-Ausdruck:**
```turtle
:BeispielShape a sh:PropertyShape ;
    ex:feldlaengenTyp feldtyp:Variabel ;
    sh:maxLength 100 .
```

**Hinweis:** Variable Feldlängen werden in SHACL nur durch `sh:maxLength` ausgedrückt (ohne `sh:minLength` oder mit `sh:minLength < sh:maxLength`).

## Verwendung in SHACL Shapes

### Metadata-Property

```turtle
ex:feldlaengenTyp a owl:ObjectProperty ;
    rdfs:label "Feldlängentyp"@de ;
    rdfs:domain sh:PropertyShape ;
    rdfs:range skos:Concept .
```

### Validation Constraint

```turtle
ex:FeldlaengenTypConstraint a sh:PropertyShape ;
    sh:path ex:feldlaengenTyp ;
    sh:in ( feldtyp:Fest feldtyp:Variabel ) ;
    sh:nodeKind sh:IRI ;
    sh:message "ex:feldlaengenTyp muss entweder feldtyp:Fest oder feldtyp:Variabel sein"@de .
```

## Statistik

**Stand:** 20. Januar 2026

| Typ | Anzahl Shapes | Prozent |
|-----|---------------|---------|
| Fest | 11 | 48% |
| Variabel | 12 | 52% |
| **Gesamt** | **23** | **100%** |

**Hinweis:** Aktuell haben nur 23 von 348 Shapes den Feldlängentyp definiert. Dies entspricht etwa 6,6% der gesamten Shapes.

## Integration

### Vokabular-Sammlung

Das Feldlängentyp-Vokabular ist Teil der DSAusländer-Vokabular-Sammlung:

```turtle
<http://bamf.de/vocabulary/dsauslaender-vocabularies> 
    owl:imports <http://bamf.de/vocabulary/feldlaengentyp> .
```

### SHACL Shapes

```turtle
@prefix feldtyp: <http://bamf.de/vocabulary/feldlaengentyp#> .
```

## Beispiele

### Festes Feld: Behördenkennzeichen (6 Zeichen)

```turtle
:AktenfuehrendeBehoerdePropertyShape a sh:PropertyShape ;
    ex:nummer "001" ;
    ex:feldname "Aktenführende Behörde" ;
    ex:feldlaengenTyp feldtyp:Fest ;
    sh:minLength 6 ;
    sh:maxLength 6 ;
    sh:pattern "^[0-9]{6}$" ;
    ex:formatVorgabe "Behördenkennzeichen" ;
    sh:datatype xsd:string .
```

### Variables Feld: Familienname (max. 100 Zeichen)

```turtle
:FamiliennamePropertyShape a sh:PropertyShape ;
    ex:nummer "004.01" ;
    ex:feldname "Familienname" ;
    ex:feldlaengenTyp feldtyp:Variabel ;
    sh:maxLength 100 ;
    sh:datatype xsd:string .
```

## SPARQL Queries

### Alle Shapes mit festem Feldlängentyp

```sparql
PREFIX ex: <http://bamf.de/shapes/metadata#>
PREFIX feldtyp: <http://bamf.de/vocabulary/feldlaengentyp#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT ?shape ?feldname ?nummer
WHERE {
    ?shape a sh:PropertyShape ;
           ex:feldlaengenTyp feldtyp:Fest ;
           ex:feldname ?feldname ;
           ex:nummer ?nummer .
}
ORDER BY ?nummer
```

### Alle Shapes mit variablem Feldlängentyp

```sparql
PREFIX ex: <http://bamf.de/shapes/metadata#>
PREFIX feldtyp: <http://bamf.de/vocabulary/feldlaengentyp#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT ?shape ?feldname ?nummer ?maxLength
WHERE {
    ?shape a sh:PropertyShape ;
           ex:feldlaengenTyp feldtyp:Variabel ;
           ex:feldname ?feldname ;
           ex:nummer ?nummer ;
           sh:maxLength ?maxLength .
}
ORDER BY ?nummer
```

### Shapes ohne Feldlängentyp (zur Identifikation fehlender Metadaten)

```sparql
PREFIX ex: <http://bamf.de/shapes/metadata#>
PREFIX sh: <http://www.w3.org/ns/shacl#>

SELECT ?shape ?feldname ?nummer
WHERE {
    ?shape a sh:PropertyShape ;
           ex:feldname ?feldname ;
           ex:nummer ?nummer .
    FILTER NOT EXISTS { ?shape ex:feldlaengenTyp ?typ }
}
ORDER BY ?nummer
```

## Nächste Schritte

1. **PDF-Extraktion:** Alle 283+ Felder aus der Datensatzbeschreibung extrahieren
2. **FIELD_SPECIFICATIONS vervollständigen:** Enhancement-Skript mit allen Feldspezifikationen ausstatten
3. **Vollständige Anwendung:** Alle ~325 verbleibenden Shapes mit Feldlängentyp versehen
4. **Dokumentation aktualisieren:** Statistik nach vollständiger Anwendung aktualisieren

## Rechtliche Grundlagen

Die Feldlängenvorgaben basieren auf der **Datensatzbeschreibung DSAusländer Version 7.0** (gültig ab 01.05.2025).

## Versionierung

- **1.0.0** (20.01.2026): Initiale Erstellung des Vokabulars
- Integration in dsauslaender-vocabularies.ttl
- Validation Constraint in SHACL Shapes hinzugefügt
- 23 PropertyShapes initial klassifiziert

## Dateien

- **Vokabular:** [vocabularies/feldlaengentyp.ttl](feldlaengentyp.ttl)
- **SHACL Shapes:** [dsauslaender-shapes.ttl](../dsauslaender-shapes.ttl)
- **Sammlung:** [vocabularies/dsauslaender-vocabularies.ttl](dsauslaender-vocabularies.ttl)
- **Enhancement-Skript:** [scripts/enhance_shapes_with_constraints.py](../scripts/enhance_shapes_with_constraints.py)
