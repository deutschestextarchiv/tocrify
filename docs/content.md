layout: true
  
<div class="my-header"></div>

<div class="my-footer">
  <table>
    <tr>
      <td>Digitale Sammlung Deutscher Kolonialismus</td>
      <td style="text-align:right"><a href="http://www.bbaw.de/forschung/digitale-sammlung-deutscher-kolonialismus/uebersicht">www.bbaw.de</a></td>
    </tr>
  </table>
</div>

---

class: title-slide

# tocrify

## Verfeinerung der Strukturierung von OCR-Volltexten durch Integration manuell erfasster Strukturelemente

| Matthias Boenig | Kay-Michael Würzner |
|:----------------:|:----------------:|:-------------------:|
| [boenig@bbaw.de](mailto:boenig@bbaw.de) | [wuerzner@bbaw.de](mailto:wuerzner@bbaw.de) |

---

# Inhalte

1. Konvertierungworkflow
  - `tocrify`: Werkzeug zur Anreicherung der OCR-Ergebnisse
  - `hocr2tei`: XSLT-Stylesheets zur Konvertierung der angereicherten OCR nach DTABf
2. DSDK-Korpus
  - aktueller Stand der Konvertierung
  - Anwendungsbeispiele der Korpusinfrastruktur des Zentrums Sprache auf die DSDK-Daten
3. Diskussion
  - nächste Schritte und ToDos
  - Optimierungsmöglichkeiten im Workflow
  - Perspektiven für die Volltextdigitalisierung in wissenschaftlichen Bibliotheken

---

class: title-slide

# Konvertierung

---

# Konvertierung - Motivation

- (proto-)typische Ausgangslage:
  + METS-XML mit (MODS-)Metadaten sowie manuellen Strukturauszeichnungen (häufig einfach „abgeschriebene“ Inhaltsverzeichnisse)
  + Bilddateien (verzeichnet im METS)
  + OCR-Dateien (auf Seitenebene verknüpft mit den Bildern)
- Ziel:
  + **adäquate** Repräsentation der Volltexte in TEI
    * *Best practice* für Textdaten in den digitalen Geisteswissenschaften
    * dokumentbezogenes Format
    * **DTA-Basisformat** (DTABf) als de-facto Standard für historische Textdaten
  + Anschluss an bestehende Forschungsinfrastrukturen

---

# Konvertierung - Baseline

- triviales Vorgehen:
  ```xml
  <tei>
    <teiHeader><!-- Informationen aus MODS --></teiHeader>
    <text>
      <body>
        <p>
          <!-- OCR-Volltext -->
        </p>
      </body>
    </text>
  </tei>
  ```
- valide aber nicht **adäquat**

---

# Konvertierung - Idee

- Nachnutzung der manuell gesammelten Strukturdaten (`<mets:structMap TYPE="LOGICAL" />`)
  ```xml
  <mets:div ID="log9156964"
            TYPE="chapter"
            LABEL="Geologische Uebersicht"
            ORDER="7"/>
  ```
- Auszeichnung der entsprechenden Volltextpassagen in der OCR
- Übernahme nach DTABf
  + Seiten- → Dokumentebene
  + *umspannende* `div`-Struktur

---

# Konvertierung - Herausforderungen

- Verknüpfung zwischen Struktur und Text auf Seitenebene (keine Lokalisierung im Text)
  + Lösungsansatz: Lokalisierung des Strukturelements auf der Seite über Textvergleich
- mangelndes Strukturauszeichnungsinventar in ABBYY-FineReader-XML
  + Lösungsansatz: Konvertierung in feingranulareres OCR-Format
- nicht standardgemäße Seitenverknüpfung in ` <mets:structLink />` durch *anonyme* IDs
  + Lösungsansatz: Auflösung der anonymen IDs
- nicht erfasste Vakatseiten und Abbildungen
  + Lösungsansatz: Ergänzung leerer ABBYY-FineReader-XML-Dateien
  
---

# Konvertierung - Workflow

1. **Konvertierung** ABBYY-FineReader-XML nach hOCR
  - mit Hilfe eines XSLT-Stylesheets (https://github.com/OCR-D/format-converters)
2. **Anreicherung** der hOCR-Dateien mit Strukturelementen
  - Python-Skript `tocrify` (https://github.com/deutschestextarchiv/tocrify)
3. **Aggregation** der Seiten- zur Dokumentebene
  - Anpassung der hOCR-Tool-Suite (https://github.com/tmbdev/hocr-tools)
4. **Konvertierung** von hOCR nach DTABf
  - mit Hilfe eines XSLT-Stylesheets (https://github.com/OCR-D/format-converters)
  - Integration der MODS-Metadaten in den TEI-Header
5. **Integration** in die Korpusinfrastruktur des Zentrums Sprache sowie in DTAQ

---

# Konvertierung - `tocrify`

- Ziel: *Lokalisierung* des Strukturelements auf der Seite (Ermittlung der Koordinaten)
- Rezept:
  + Vergleich des zu lokalisierenden Textes `\(t\)` mit allen Position in der OCR `\(o_i\in O=o_1\ldots o_n\)`
  + minimaler Editierabstand zwischen `\(t\)` und `\(o_i\ldots o_{i+|t|}\)` als Platzierungskriterium
  + Inklusion aller Zeilen, die Teile der optimalen OCR-Sequenz enthalten
- Auszeichnung der ermittelten Zeilen als `TYPE` (i.e. Strukturtyp nach METS)

---

# Konvertierung - Probleme

---

class: title-slide

# Danke für Ihre Aufmerksamkeit
