import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def benchmark_governance(df: pd.DataFrame) -> None:
    """
    Ermittelt den sektoralen Median der GovernancePillarScores für ein gewähltes Jahr
    und berechnet für jedes Unternehmen die Abweichung vom jeweiligen Branchenwert.
    Die Ergebnisse werden anschließend in einem interaktiven Boxplot dargestellt.
    """

    st.header("Governance-Benchmarking nach Branche")

    # Auswahl des Analysejahres durch den Nutzer
    jahre = df["Year"].dropna().unique()
    jahre.sort()
    selected_year = st.selectbox("Analysejahr auswählen", jahre)

    # Filterung der Daten auf das gewählte Jahr
    df_filtered = df[df["Year"] == selected_year].copy()

    # Vorabprüfung: Sind alle benötigten Spalten vorhanden?
    notwendige_spalten = ["Company Name", "Sektor", "GovernancePillarScore"]
    if not all(spalte in df_filtered.columns for spalte in notwendige_spalten):
        st.error("Die für das Benchmarking erforderlichen Spalten fehlen im Datensatz.")
        return

    # Berechnung des Median-Scores je Branche
    mediane = df_filtered.groupby("Sektor")["GovernancePillarScore"].median()

    # Differenz jedes Unternehmens zum Branchenmedian berechnen
    df_filtered["GovernanceDeltaToMedian"] = df_filtered.apply(
        lambda row: row["GovernancePillarScore"] - mediane.get(row["Sektor"], np.nan),
        axis=1
    )

    # Boxplot der Governance-Scores nach Sektor (inkl. Ausreißerpunkte)
    fig = px.box(
        df_filtered,
        x="Sektor",
        y="GovernancePillarScore",
        points="all",
        title=f"Verteilung der Governance-Scores nach Branche ({selected_year})",
        labels={"GovernancePillarScore": "Governance Score"},
        color="Sektor"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Optionale Tabellenansicht der berechneten Abweichungen
    with st.expander("Tabelle mit Score-Abweichungen einblenden"):
        st.dataframe(df_filtered[[
            "Company Name", "Sektor", "GovernancePillarScore", "GovernanceDeltaToMedian"
        ]])