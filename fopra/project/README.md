# Feuerwehr-Berichts-Analyse-System

Ein Python-basiertes System zur automatischen Analyse von Feuerwehr-Einsatzberichten mit BERT und Neo4j.

## Features

- Automatische Extraktion von Einsatzinformationen mit BERT
- Strukturierte Speicherung in Neo4j Graphdatenbank
- Analyse von:
  - Einsatzart
  - Ort
  - Datum
  - Dauer
  - Beteiligte Einheiten
  - Einsatzverlauf

## Installation

1. **Python-Installation**
   - Python 3.8 oder höher wird benötigt

2. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

1. **Programm starten**
   ```bash
   python main.py
   ```

## Ausgabe

- Extrahierte Informationen werden in Neo4j gespeichert
- Logs werden in `logs/scraping.log` geschrieben