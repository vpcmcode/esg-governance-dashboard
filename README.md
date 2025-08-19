# ESG-Governance-Dashboard

Dieses Projekt stellt ein interaktives Dashboard bereit, das den Zusammenhang zwischen ESG-Governance-Scores und der Aktienrendite von Unternehmen des S&P 500 analysiert. Es wurde im Rahmen einer Masterarbeit in Wirtschaftsinformatik nach dem Design-Science-Research-Ansatz entworfen und umgesetzt

## Online-Version (empfohlen)

Das Dashboard ist ohne lokale Installation hier erreichbar:  
https://esg-governance-dashboard-qrmes9bveb5acu93hzduuv.streamlit.app/

<details>
<summary><strong>Optionale lokale Ausführung (für Reproduzierbarkeit)</strong></summary>

Voraussetzungen: Python 3.11, Abhängigkeiten aus <code>requirements.txt</code>.  
Die ESG-Datei muss unter <code>data/esg_dataset.xlsx</code> liegen.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
streamlit run main.py
```

Das Dashboard öffnet sich im Browser (standardmäßig http://localhost:8501).
</details>

## Zielsetzung und Funktionsumfang

Das Dashboard unterstützt explorative Analysen, um zu prüfen, ob und in welchem Umfang Governance-Scores mit der Aktienperformance zusammenhängen. Es bietet Filter nach Jahr, Sektor und Unternehmen sowie verschiedene Darstellungen, unter anderem Streudiagramme mit Regressionslinie, unternehmensspezifische Korrelationen mit r- und p-Wert, gruppierte Auswertungen nach Quintilen, Zeitreihen und Benchmarks.

## Technologischer Rahmen

Entwickelt mit Python 3.11. Zentrale Bibliotheken:
- streamlit
- pandas
- plotly
- numpy
- openpyxl
- statsmodels

Optionale Bibliotheken (im Projekt enthalten, aber nicht zwingend benötigt): scipy, matplotlib, xlsxwriter.  
Alle Abhängigkeiten sind in `requirements.txt` hinterlegt.

## Datenformat

Die ESG-Eingabedatei muss im Projektordner unter `data/esg_dataset.xlsx` liegen. Eigene Datensätze können verwendet werden, sofern die Spaltenstruktur der Originaldatei beibehalten wird.
