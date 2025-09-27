import pandas as pd
import streamlit as st
import plotly.express as px

def governance_analysis_view(df: pd.DataFrame):
    """
    Analyse der Jahresrenditen nach Governance-Score-Quintilen.
    """

    st.subheader("Governance-Score vs. Rendite (nach Quintilen)")

    # Jahresauswahl
    years = sorted(df["Year"].dropna().unique())
    selected_years = st.multiselect("Analysejahre", options=years, default=years)

    # Filterung nach Jahr
    df_filtered = df[df["Year"].isin(selected_years)].copy()

    # Pflichtspalten prüfen
    required_cols = ["GovernancePillarScore", "AnnualReturnPct", "Company Name"]
    if not all(col in df_filtered.columns for col in required_cols):
        st.error("Eine oder mehrere benötigte Spalten fehlen.")
        return

    # Umwandlung in numerische Werte
    df_filtered["GovernancePillarScore"] = pd.to_numeric(df_filtered["GovernancePillarScore"], errors="coerce")
    df_filtered["AnnualReturnPct"] = pd.to_numeric(df_filtered["AnnualReturnPct"], errors="coerce")
    df_filtered.dropna(subset=["GovernancePillarScore", "AnnualReturnPct"], inplace=True)

    if df_filtered.empty:
        st.warning("Keine auswertbaren Daten für die gewählten Jahre.")
        return

    # Einteilung in Quintile
    try:
        df_filtered["Governance-Gruppe"] = pd.qcut(
            df_filtered["GovernancePillarScore"],
            q=5,
            labels=["Sehr niedrig", "Niedrig", "Mittel", "Hoch", "Sehr hoch"]
        )
    except ValueError:
        st.warning("Zu wenige Datenpunkte zur Bildung von Quintilen.")
        return

    # Berechnung gruppierter Statistiken
    summary = (
        df_filtered.groupby("Governance-Gruppe", observed=True)["AnnualReturnPct"]
        .agg(["mean", "std", "count"])
        .rename(columns={
            "mean": "Ø Rendite",
            "std": "Standardabweichung",
            "count": "Anzahl Unternehmen"
        })
        .reset_index()
    )
    summary["Governance-Gruppe"] = summary["Governance-Gruppe"].astype(str)

    summary["Ø Rendite"] = summary["Ø Rendite"].round(2)
    summary["Standardabweichung"] = summary["Standardabweichung"].round(4)

    # Visualisierung
    fig = px.bar(
        summary,
        x="Governance-Gruppe",
        y="Ø Rendite",
        text="Ø Rendite",
        color="Governance-Gruppe",
        title="Durchschnittliche Rendite nach Governance-Quintilen",
        labels={
            "Governance-Gruppe": "Governance-Score (Quintil)",
            "Ø Rendite": "Ø Jahresrendite (%)"
        },
        height=500
    )

    fig.update_layout(
        xaxis=dict(tickfont=dict(size=14)),
        yaxis=dict(tickfont=dict(size=14))
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabelle
    st.markdown("### Statistische Kennzahlen je Gruppe")
    st.dataframe(summary.set_index("Governance-Gruppe"), use_container_width=True)