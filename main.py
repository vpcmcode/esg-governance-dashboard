import streamlit as st
import pandas as pd
import io

# Cachen und laden des Datasets
DATA_PATH = "data/esg_dataset.xlsx"

@st.cache_data(show_spinner=False)
def lade_datenquelle(source: bytes | str) -> pd.DataFrame:
    """Lädt ein Excel entweder von Pfad (str) oder aus Bytes (Upload) und cached das Ergebnis."""
    if isinstance(source, str):
        return pd.read_excel(source, engine="openpyxl")
    elif isinstance(source, (bytes, bytearray)):
        bio = io.BytesIO(source)
        return pd.read_excel(bio, engine="openpyxl")
    else:
        raise TypeError("Unsupported source type for lade_datenquelle")

# Grundlayout
st.set_page_config(
    page_title="ESG-Governance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.markdown("## Datenquelle")
    OPTION_SAMPLE = "ESG-Dataset S&P 500 (2015-2025)"
    OPTION_UPLOAD = "Eigene Datei hochladen (Bitte Template benutzen)"
    quelle = st.radio(
        "Quelle wählen",
        [OPTION_SAMPLE, OPTION_UPLOAD],
        index=0
    )
    uploaded_file = None
    if quelle == OPTION_UPLOAD:
        uploaded_file = st.file_uploader("Excel-Datei (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            st.success("Datei geladen – die Auswertungen beziehen sich auf die hochgeladene Datei.")
        else:
            st.info("Bitte das Template benutzen, vollständig befüllen und als .xlsx-Datei hochladen um die Funktionalität zu gewährleisten.")

# Datenvorbereitung
from modules.filters import filter_data
from modules.calculations import calculate_returns

# Analysefunktionen
from modules.governance_impact import governance_vs_rendite
from modules.governance_analysis import governance_analysis_view
from modules.correlation import correlation_analysis_view
from modules.benchmark import benchmark_governance
from modules.timeseries import governance_timeseries

# Laden der Datenquelle (Upload hat Vorrang vor Beispieldaten)
try:
    if uploaded_file is not None:
        df_raw = lade_datenquelle(uploaded_file.read())
    else:
        df_raw = lade_datenquelle(DATA_PATH)
except FileNotFoundError:
    st.error(f"Die Datenquelle '{DATA_PATH}' ist nicht verfügbar. Bitte stellen Sie sicher, dass die Datei im Repository vorhanden ist.")
    st.stop()
except Exception as e:
    st.error(f"Fehler beim Einlesen der Datei: {e}")
    st.stop()

# Vorverarbeitung und Aggregation
df_filtered = filter_data(df_raw)
df = calculate_returns(df_filtered)

# Tabstruktur
tabs = st.tabs([
    "Governance-Scores und Renditeentwicklung im Vergleich",
    "Governance-Quintile",
    "Korrelationsanalyse",
    "Branchen-Benchmarking",
    "Renditeentwicklung im Zeitverlauf"
])

with tabs[0]:
    governance_vs_rendite(df)

with tabs[1]:
    governance_analysis_view(df)

with tabs[2]:
    correlation_analysis_view(df)

with tabs[3]:
    benchmark_governance(df)

with tabs[4]:
    governance_timeseries(df)