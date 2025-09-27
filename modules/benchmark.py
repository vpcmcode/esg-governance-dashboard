import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def benchmark_governance(df: pd.DataFrame) -> None:
    """
    Visualisiert die Governance-Scores nach Branchenzugehörigkeit und zeigt auf,
    wie stark einzelne Unternehmen vom Median ihrer Branche abweichen.
    """

    st.header("Governance-Benchmarking nach Branche")

    # Verfügbare Jahre aus dem Datensatz extrahieren
    jahre = df["Year"].dropna().unique()
    jahre.sort()
    selected_year = st.selectbox("Analysejahr auswählen", jahre)

    # Datensatz auf das ausgewählte Jahr begrenzen
    df_filtered = df[df["Year"] == selected_year].copy()

    # Prüfen, ob alle benötigten Spalten vorhanden sind
    benoetigt = ["Company Name", "Sektor", "GovernancePillarScore"]
    if not all(spalte in df_filtered.columns for spalte in benoetigt):
        st.error("Mindestens eine erforderliche Spalte fehlt im Datensatz.")
        return

    # Berechnung des Median-Scores je Branche
    median_scores = df_filtered.groupby("Sektor")["GovernancePillarScore"].median()

    # Abweichung jedes Unternehmens vom jeweiligen Branchenmedian
    df_filtered["GovernanceDeltaToMedian"] = df_filtered.apply(
        lambda row: row["GovernancePillarScore"] - median_scores.get(row["Sektor"], np.nan),
        axis=1
    )

    # Boxplot zur Verteilung der Scores nach Branche
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

    # Erweiterbare Tabelle mit den Abweichungswerten
    with st.expander("Tabelle mit Score-Abweichungen einblenden"):
        basis = [
            "Company Name", "Sektor", "GovernancePillarScore", "GovernanceDeltaToMedian"
        ]
        table_df = df_filtered[basis].copy()

        # Aggregation auf einen Eintrag je Unternehmen
        only_once = st.checkbox("Mittelwert je Unternehmen)", value=True)
        if only_once:
            grouped = (
                table_df
                .groupby(["Company Name", "Sektor"], as_index=False)
                .agg({
                    "GovernancePillarScore": "mean",
                    "GovernanceDeltaToMedian": "mean"
                })
            )
            grouped["Anzahl_Einträge"] = table_df.groupby(["Company Name", "Sektor"]).size().values
            table_df = grouped

        # Filterfunktion für Unternehmen oder Branchen
        suchbegriff = st.text_input("Suche (Unternehmen/Sektor)", value="")
        if suchbegriff:
            maske = (
                table_df["Company Name"].str.contains(suchbegriff, case=False, na=False)
                | table_df["Sektor"].str.contains(suchbegriff, case=False, na=False)
            )
            table_df = table_df[maske]

        # Sortierung nach Abweichung
        if "GovernanceDeltaToMedian" in table_df.columns:
            table_df = table_df.sort_values("GovernanceDeltaToMedian", ascending=False)

        # Formatierung der numerischen Spalten
        for spalte in ["GovernancePillarScore", "GovernanceDeltaToMedian"]:
            if spalte in table_df.columns:
                table_df[spalte] = table_df[spalte].apply(
                    lambda x: "" if pd.isna(x) else f"{x:.0f}"
                )

        # Umbenennung der Spalten für die Darstellung
        display_df = table_df.rename(columns={
            "Company Name": "Unternehmen",
            "GovernancePillarScore": "Governance Score",
            "GovernanceDeltaToMedian": "Abweichung"
        })

        display_df = display_df.reset_index(drop=True)
        st.dataframe(display_df, use_container_width=True)