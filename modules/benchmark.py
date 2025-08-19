import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def benchmark_governance(df: pd.DataFrame) -> None:
    """
    Zeigt, wie stark einzelne Unternehmen im Hinblick auf ihren GovernancePillarScore
    vom Median ihrer Branche abweichen. Dafür wird ein Jahr ausgewählt, die Daten
    gefiltert und die Abweichungen visualisiert.
    """

    st.header("Governance-Benchmarking nach Branche")

    # Jahr auswählen
    jahre = df["Year"].dropna().unique()
    jahre.sort()
    selected_year = st.selectbox("Analysejahr auswählen", jahre)

    # Daten auf das gewählte Jahr filtern
    df_filtered = df[df["Year"] == selected_year].copy()

    # Prüfen auf alle notwenidigen Spalten
    notwendige_spalten = ["Company Name", "Sektor", "GovernancePillarScore"]
    if not all(spalte in df_filtered.columns for spalte in notwendige_spalten):
        st.error("Es fehlen eine oder mehrere erforderliche Spalten im Datensatz.")
        return

    # Median-Score je Branche berechnen
    mediane = df_filtered.groupby("Sektor")["GovernancePillarScore"].median()

    # Abweichung zum Median berechnen
    df_filtered["GovernanceDeltaToMedian"] = df_filtered.apply(
        lambda row: row["GovernancePillarScore"] - mediane.get(row["Sektor"], np.nan),
        axis=1
    )

    # Boxplot erstellen
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

    # Tabelle mit Abweichungen anzeigen
    with st.expander("Tabelle mit Score-Abweichungen einblenden"):
        st.dataframe(df_filtered[[
            "Company Name", "Sektor", "GovernancePillarScore", "GovernanceDeltaToMedian"
        ]])
