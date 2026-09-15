# Business Intelligence & Prozessanalyse: E-Commerce Lieferkette & Retouren

## 1. Ausgangssituation (Initial Situation)

Ein mittelständisches deutsches E-Commerce-Unternehmen verzeichnet eine steigende Retourenquote und sinkende Kundenzufriedenheit. Es fehlt an Transparenz bezüglich der Ursachen von Lieferverzögerungen und Retouren in der Logistikkette.

## 2. Zielsetzung (Project Goals)

- Aufbau eines reproduzierbaren Python-Pipelines für Ingestion, Datenqualitätsprüfung und Laden der Daten.
- Datenschutzorientierte Verarbeitung: Personenbezogene Kundendaten (Name, E-Mail) werden im Ingestion-Schritt per SHA-256-Hashing pseudonymisiert, bevor sie das Analyse-System erreichen.
- Relationales Star Schema, sowohl in SQLite (für SQL-Analysen) als auch in Power BI (für das Dashboard).
- Nachvollziehbare Datenqualitätsprüfung mit dokumentierten, quarantänierten (nicht stillschweigend gelöschten) fehlerhaften Datensätzen.
- Business-relevante SQL-Auswertungen zu Lieferverzögerungen, Retourenquote und Kosten.

## 3. Datenarchitektur

- **Technologie-Stack:** Python (Pandas, Faker), SQLite, SQL, Power BI (DAX), Bash, Git.
- **Datenschutz:** Personenbezogene Daten (PII wie Namen und E-Mails) werden direkt im Ingestion-Skript (`generate_data.py`) mittels SHA-256-Hashing pseudonymisiert, bevor Kundendaten weiterverarbeitet werden. Es handelt sich um eine technische Pseudonymisierungsmaßnahme, keine rechtliche DSGVO-Zertifizierung.
- **Pipeline:** `generate_data.py` (Ingestion/Rohdaten) → `load_to_db.py` (Datenqualitätsprüfung + Laden nach SQLite) → `run_queries.py` (SQL-Auswertungen) → Power BI (Dashboard).

## 4. Datenmodell (Star Schema)

- **Fact_Orders:** Transaktionsdaten (Bestelldatum, Lieferdatum, Logistikdienstleister, Retourenstatus).
- **Dim_Products:** Produktkategorien, Preise, Selbstkosten.
- **Dim_Customers:** Pseudonymisierte Kundendaten (PLZ, Bundesland).

Definiert in [`sql/schema.sql`](sql/schema.sql).

## 5. Datenqualität (Data Quality)

Die Rohdaten enthalten realistische, absichtlich eingebaute Fehler (siehe `generate_data.py`), um eine echte Validierung zu ermöglichen statt einer bereits perfekt sauberen Datenbasis:

- doppelte Kunden- und Bestelldatensätze (z. B. durch doppelten Import),
- fehlende Postleitzahlen,
- negative Versandkosten (Dateneingabefehler),
- Lieferdatum vor Bestelldatum (logisch unmögliche Datensätze).

`load_to_db.py` prüft jede dieser Regeln, **quarantäniert** betroffene Zeilen statt sie stillschweigend zu löschen (`reports/quarantined_customers.csv`, `reports/quarantined_orders.csv`) und schreibt einen zusammenfassenden Bericht nach [`reports/data_quality_report.md`](reports/data_quality_report.md). Nur geprüfte, saubere Daten werden in die SQLite-Datenbank geladen.

## 6. SQL-Analysen

[`sql/business_queries.sql`](sql/business_queries.sql) enthält die SQL-Abfragen, die die Kernerkenntnisse direkt aus der Datenbank ableiten (nicht nur aus Power BI). `run_queries.py` führt sie aus und schreibt die Ergebnisse nach [`reports/sql_findings.md`](reports/sql_findings.md).

## 7. Kernerkenntnisse (Key Findings)

1. **Logistik-Engpass:** Der Dienstleister Hermes weist mit durchschnittlich ~4,3 Tagen signifikant höhere Lieferzeiten auf als DHL oder DPD (~2 Tage).
2. **Kausalität von Verzögerung & Retouren:** Bei Lieferungen mit ≥ 5 Tagen Verzögerung ist *"Zu spät geliefert"* mit Abstand der häufigste Retourengrund.
3. **Fokuskategorie Bekleidung:** Die Retourenquote in der Kategorie *Bekleidung* liegt bei knapp 39 %, deutlich über allen anderen Kategorien.

(Exakte Zahlen: siehe `reports/sql_findings.md`, reproduzierbar über die Pipeline.)

## 8. Handlungsempfehlungen & Wirtschaftlicher Nutzen

- **Kostenreduktion:** Neuverhandlung der SLAs mit Hermes oder Umverteilung des Versandvolumens zur Reduktion verspätungsbedingter Retouren.
- **Prozessoptimierung:** Einführung präziserer Größentabellen im Shop zur Senkung der Retourenquote in der Kategorie Bekleidung.

## 9. Reproduzierbarkeit

```bash
pip install -r requirements.txt
bash run_pipeline.sh
```

Das Skript generiert die Rohdaten, führt die Datenqualitätsprüfung durch, lädt die sauberen Daten nach `ecommerce.db` und schreibt beide Berichte nach `reports/`. Das bestehende Power-BI-Dashboard (`Lieferketten_Retouren_Analyse.pbix`) liest dieselben CSV-Dateien.

## 10. Projektstruktur

```
.
├── generate_data.py           # Ingestion / Rohdaten-Generierung
├── load_to_db.py               # Datenqualitätsprüfung + Laden nach SQLite
├── run_queries.py               # Führt SQL-Analysen aus
├── run_pipeline.sh              # Orchestriert die gesamte Pipeline
├── sql/
│   ├── schema.sql                # Star-Schema-Definition
│   └── business_queries.sql      # Business-SQL-Abfragen
├── reports/                    # Generierte Berichte (Data Quality, SQL Findings)
├── Dim_Customers.csv / Dim_Products.csv / Fact_Orders.csv
├── Lieferketten_Retouren_Analyse.pbix
└── requirements.txt
```
