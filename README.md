# Business Intelligence & Prozessanalyse: E-Commerce Lieferkette & Retouren

## 1. Ausgangssituation (Initial Situation)
Ein mittelständisches deutsches E-Commerce-Unternehmen verzeichnet eine steigende Retourenquote und sinkende Kundenzufriedenheit. Es fehlt an Transparenz bezüglich der Ursachen von Lieferverzögerungen und Retouren in der Logistikkette.

## 2. Zielsetzung (Project Goals)
* Aufbau eines automatisierten ETL-Prozesses in Python.
* Einhaltung der **DSGVO (Datenschutz-Grundverordnung)** durch Anonymisierung von Kundendaten.
* Entwicklung eines relationalen **Sternschemas (Star Schema)** in Power BI.
* Bereitstellung interaktiver Dashboards zur Identifikation von Engpässen und Optimierungspotenzialen.

## 3. Datenarchitektur & DSGVO (Data Architecture & GDPR)
* **Technologie-Stack:** Python (Pandas, Faker), Power BI, DAX, Git.
* **DSGVO-Konformität:** Personenbezogene Daten (PII wie Namen und E-Mails) wurden direkt im Python-ETL-Skript mittels **SHA-256 Hashing** pseudonymisiert, bevor die Daten ins BI-System geladen wurden.

## 4. Power BI Datenmodell (Star Schema)
* **Fact_Orders:** Transaktionsdaten (Bestelldatum, Lieferdatum, Logistikdienstleister, Retourenstatus).
* **Dim_Products:** Produktkategorien, Preise, Selbstkosten.
* **Dim_Customers:** Anonymisierte Kundendaten (PLZ, Bundesland).
* **Dim_Date:** Zeitdimension für Zeitreihenanalysen.

## 5. Kernerkenntnisse & Prozessanalyse (Key Findings)
1. **Logistik-Engpass:** Der Dienstleister Hermes weist mit durchschnittlich ~5–6 Tagen signifikant höhere Lieferzeiten auf als DHL oder DPD (~2–3 Tage).
2. **Kausalität von Verzögerung & Retouren:** Späte Lieferungen (≥ 5 Tage) erhöhen die Wahrscheinlichkeit einer Retoure mit dem Grund *"Zu spät geliefert"* um über 20 %.
3. **Fokuskategorie Bekleidung:** Die Retourenquote in der Kategorie *Bekleidung* liegt bei über 30 %, hauptsächlich getrieben durch *"Passt nicht"*.

## 6. Handlungsempfehlungen & Wirtschaftlicher Nutzen (Business ROI)
* **Kostenreduktion:** Wechsel oder Neuverhandlung der SLAs für den Versanddienstleister Hermes zur Einsparung von Logistik- und Retourenkosten.
* **Prozessoptimierung:** Einführung präziserer Größentabellen im Shop zur Senkung der Retouren in der Kategorie Bekleidung.