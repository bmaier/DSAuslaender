# Sensitivitätsstufen-Vokabular

## Übersicht

Das Vokabular für Sensitivitätsstufen (Sensitivity Levels) klassifiziert die Sensitivität von Datenfeldern im DSAusländer-Register gemäß Datenschutz- und Sicherheitsanforderungen.

## Dateien

- **`sensitivitaet.ttl`** - Vollständiges SKOS-Vokabular mit allen Sensitivitätsstufen
- URI: `http://bamf.de/vocabulary/sensitivitaet`

## Werteliste

Das Vokabular definiert folgende vier Sensitivitätsstufen:

### 1. Öffentlich (Public)
- **URI**: `http://bamf.de/vocabulary/sensitivitaet#Oeffentlich`
- **Notation**: `0`
- **Label**: "öffentlich" (de), "public" (en)
- **Definition**: Daten ohne Zugriffsbeschränkungen, die öffentlich verfügbar sind oder sein können
- **Beispiel**: Allgemeine Statistiken, öffentliche Bekanntmachungen

### 2. Intern (Internal)
- **URI**: `http://bamf.de/vocabulary/sensitivitaet#Intern`
- **Notation**: `1`  
- **Label**: "intern" (de), "internal" (en)
- **Definition**: Daten für den internen Gebrauch innerhalb der Behörde
- **Beispiel**: Interne Verwaltungsinformationen, Aktenführung, Verfahrensdaten
- **Hierarchie**: Breiter als "öffentlich"

### 3. Vertraulich (Confidential)
- **URI**: `http://bamf.de/vocabulary/sensitivitaet#Vertraulich`
- **Notation**: `2`
- **Label**: "vertraulich" (de), "confidential" (en)
- **Definition**: Vertrauliche Daten mit beschränktem Zugriff nach DSGVO und BDSG
- **Beispiel**: Personenbezogene Daten, Aufenthaltsstatus, Familieninformationen, Adressdaten
- **Rechtsgrundlage**: Art. 4 Nr. 1 DSGVO (personenbezogene Daten)
- **Hierarchie**: Breiter als "intern"

### 4. Streng vertraulich (Strictly Confidential)
- **URI**: `http://bamf.de/vocabulary/sensitivitaet#StrengVertraulich`
- **Notation**: `3`
- **Label**: "streng vertraulich" (de), "strictly confidential" (en)
- **Alternative Labels**: "hochsensibel" (de), "highly sensitive" (en)
- **Definition**: Höchst sensible Daten mit strengsten Zugriffsbeschränkungen (Art. 9 DSGVO)
- **Beispiel**: Asylgründe, Gesundheitsdaten, biometrische Daten, besondere Schutzbedürftigkeit, Opfer von Menschenhandel
- **Rechtsgrundlage**: Art. 9 DSGVO (besondere Kategorien personenbezogener Daten)
- **Schutzmaßnahmen**: Höchste Berechtigungsstufe, Need-to-know-Prinzip, besondere technische und organisatorische Maßnahmen nach Art. 32 DSGVO
- **Hierarchie**: Breiter als "vertraulich"

## Hierarchie

Die Sensitivitätsstufen bilden eine hierarchische Struktur mittels `skos:broader`:

```
Öffentlich (0)
  ↑ broader
Intern (1)
  ↑ broader  
Vertraulich (2)
  ↑ broader
Streng vertraulich (3)
```

## Verwendung in SHACL Shapes

In den SHACL Shapes wird `ex:sensitivitaet` als String-Literal verwendet:

```turtle
:PersonNameShape a sh:PropertyShape ;
    sh:path :nachname ;
    ex:sensitivitaet "vertraulich" ;  # String-Wert
    ex:nummer "005" ;
    ...
```

## Verwendung in Ontologie

Die Ontologie referenziert das Vokabular via `rdfs:seeAlso`:

```turtle
<http://bamf.de/ontology/dsauslaender> a owl:Ontology ;
    rdfs:seeAlso <http://bamf.de/vocabulary/sensitivitaet> ;
    ...
```

## Integration

Das Sensitivitäts-Vokabular ist in die Haupt-Vokabular-Sammlung integriert:

- Importiert in `dsauslaender-vocabularies.ttl`
- Referenziert in `dsauslaender-ontology.ttl`

## Abfragen (SPARQL)

### Alle Sensitivitätsstufen auflisten

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?labelDE ?labelEN ?notation ?definition
WHERE {
  ?concept skos:inScheme <http://bamf.de/vocabulary/sensitivitaet> .
  ?concept skos:prefLabel ?labelDE FILTER(lang(?labelDE) = "de") .
  ?concept skos:prefLabel ?labelEN FILTER(lang(?labelEN) = "en") .
  ?concept skos:notation ?notation .
  ?concept skos:definition ?definition FILTER(lang(?definition) = "de") .
}
ORDER BY ?notation
```

### Hierarchie abfragen

```sparql
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX sens: <http://bamf.de/vocabulary/sensitivitaet#>

SELECT ?level ?label ?broader ?broaderLabel
WHERE {
  ?level skos:inScheme <http://bamf.de/vocabulary/sensitivitaet> .
  ?level skos:prefLabel ?label FILTER(lang(?label) = "de") .
  OPTIONAL {
    ?level skos:broader ?broader .
    ?broader skos:prefLabel ?broaderLabel FILTER(lang(?broaderLabel) = "de") .
  }
}
ORDER BY ?level
```

## Aktualisierung in SHACL

Um die numerischen Notationen statt String-Literale in SHACL zu verwenden:

```turtle
# Aktuell (String)
ex:sensitivitaet "vertraulich" ;

# Optional (mit Referenz zum SKOS Concept)
ex:sensitivitaetKonzept sens:Vertraulich ;
ex:sensitivitaetstufe 2 ;  # Numerische Notation
```

## Statistiken

Nach Analyse der `dsauslaender-shapes.ttl`:

- **Öffentlich**: 1 Feld (0.3%)
- **Intern**: ~50 Felder (14.4%)
- **Vertraulich**: ~280 Felder (80.5%)
- **Streng vertraulich**: ~17 Felder (4.9%)

Die meisten Datenfelder (über 80%) sind als "vertraulich" klassifiziert, da sie personenbezogene Daten gemäß Art. 4 Nr. 1 DSGVO enthalten.

## Rechtliche Grundlagen

- **DSGVO**: Datenschutz-Grundverordnung (EU) 2016/679
  - Art. 4 Nr. 1: Definition personenbezogener Daten
  - Art. 9: Besondere Kategorien personenbezogener Daten
  - Art. 32: Sicherheit der Verarbeitung
- **BDSG**: Bundesdatenschutzgesetz
- **AufenthG**: Aufenthaltsgesetz
- **AZRG**: AZR-Gesetz (Ausländerzentralregister-Gesetz)

## Version

- **Created**: 2025-01-20
- **Modified**: 2025-01-20
- **Creator**: BAMF
- **License**: CC BY 4.0
