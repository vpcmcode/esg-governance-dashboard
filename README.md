# ESG-Governance-Dashboard

Dieses Projekt enthält ein interaktives Analyse-Dashboard zur Untersuchung des Zusammenhangs zwischen ESG-Governance-Scores und der Aktienrendite von Unternehmen im S&P 500. Die Umsetzung erfolgte im Rahmen einer Masterarbeit im Bereich Wirtschaftsinformatik mit einem gestaltungsorientierten Forschungsansatz (Design Science Research).

## Inhalt

Das Repository enthält den vollständigen Python-Code zur Durchführung der Analyse, inklusive Datenfilterung, Visualisierung, Benchmarking und Zeitreihenbetrachtung. Die Anwendung basiert auf Streamlit und ist sowohl lokal ausführbar als auch für die Veröffentlichung auf Streamlit Cloud geeignet.

## Voraussetzungen

**Python-Version:** 3.10 oder höher

**Benötigte Pakete:** (siehe `requirements.txt`)
- streamlit
- pandas
- plotly
- openpyxl
- numpy
- statsmodels

Optional (nicht zwingend notwendig, aber enthalten):
- matplotlib
- xlsxwriter
- scipy

## Lokale Ausführung

# ESG-Governance Dashboard

Dieses Projekt ist im Rahmen meiner Masterarbeit entstanden. Ziel war es, ein interaktives Dashboard zu entwickeln, das den Zusammenhang zwischen ESG-Governance-Werten und der Aktienrendite im S&P 500 untersucht. Die Umsetzung erfolgte mit Python, Streamlit und Plotly. Grundlage war ein gestaltungsorientierter wissenschaftlicher Ansatz.

## Ziel des Dashboards

Mit dem Tool lassen sich unterschiedliche Auswertungen vornehmen, um zu prüfen, ob und in welchem Umfang sich Governance-Scores auf die Performance von Aktien auswirken. Die Daten lassen sich nach Jahr, Sektor und Unternehmen filtern. Die Visualisierungen decken verschiedene Analyseformen ab, unter anderem Korrelationen, Gruppenauswertungen, Zeitverläufe und Benchmarks.

## Verwendete Bibliotheken

- Python 3.11
- streamlit
- pandas
- plotly
- openpyxl
- numpy
- scipy
- statsmodels
- matplotlib
- xlsxwriter

## Datenformat

Die zugrunde liegende Excel-Datei mit den ESG-Daten muss im Projektordner im Verzeichnis `data` liegen und den Dateinamen `esg_dataset.xlsx` tragen:

```
data/esg_dataset.xlsx
```

Eigene Dateien können verwendet werden, solange die Grundstruktur beibehalten wird.

## Projekt lokal starten

1. Projekt herunterladen oder klonen
2. Virtuelle Umgebung anlegen:

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

3. Pakete installieren:

```bash
pip install -r requirements.txt
```

4. Streamlit starten:

```bash
streamlit run main.py
```

Das Dashboard öffnet sich dann im Browser, meist unter `http://localhost:8501`.

## Externe Version

Zur Bewertung wurde das Dashboard zusätzlich online veröffentlicht. So kann es auch ohne lokale Installation über eine Streamlit-Webanwendung geöffnet werden. Link: https://esg-governance-dashboard-qrmes9bveb5acu93hzduuv.streamlit.app/
