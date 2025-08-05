import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def governance_timeseries(df: pd.DataFrame):
    """
    Visualisiert die Entwicklung von Governance-Scores und Jahresrenditen im Zeitverlauf.
    Ermöglicht wahlweise die Darstellung nach Einzelunternehmen oder aggregiert nach Sektor.
    """

    st.subheader("Zeitliche Entwicklung von Governance-Score und Rendite")

    # Auswahl des Modus: Einzelunternehmen oder Sektor
    modus = st.radio("Darstellungsmodus", ["Einzelunternehmen", "Sektortrends"], horizontal=True)

    if modus == "Einzelunternehmen":
        companies = df["Company Name"].dropna().unique()
        selected = st.multiselect("Unternehmen auswählen", sorted(companies), default=sorted(companies)[:1])

        if not selected:
            st.warning("Bitte mindestens ein Unternehmen auswählen.")
            return

        df_filtered = df[df["Company Name"].isin(selected)]
        cols_needed = ["Year", "GovernancePillarScore", "AnnualReturnPct", "Company Name"]
        if not all(col in df_filtered.columns for col in cols_needed):
            st.error("Fehlende Spalten – erforderlich: Year, GovernancePillarScore, AnnualReturnPct, Company Name")
            return

        df_filtered = df_filtered[cols_needed].dropna().sort_values("Year")
        if df_filtered.empty:
            st.warning("Keine gültigen Daten gefunden.")
            return

        fig = go.Figure()
        for firm in selected:
            data = df_filtered[df_filtered["Company Name"] == firm]
            fig.add_trace(go.Scatter(
                x=data["Year"],
                y=data["GovernancePillarScore"],
                name=f"{firm} – Governance-Score",
                mode="lines+markers",
                yaxis="y1"
            ))
            fig.add_trace(go.Scatter(
                x=data["Year"],
                y=data["AnnualReturnPct"],
                name=f"{firm} – Jahresrendite (%)",
                mode="lines+markers",
                yaxis="y2"
            ))

        fig.update_layout(
            title="Zeitliche Entwicklung: Governance & Rendite (Einzelunternehmen)",
            xaxis_title="Jahr",
            yaxis=dict(title="Governance-Score", side="left"),
            yaxis2=dict(title="Rendite (%)", side="right", overlaying="y", showgrid=False),
            legend=dict(x=0.01, y=0.99),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    elif modus == "Sektortrends":
        sektoren = df["Sektor"].dropna().unique()
        selected_sectors = st.multiselect("Sektoren auswählen", sorted(sektoren), default=sorted(sektoren)[:3])

        if not selected_sectors:
            st.warning("Bitte mindestens einen Sektor auswählen.")
            return

        df_sector = df[df["Sektor"].isin(selected_sectors)].copy()
        df_sector = df_sector.dropna(subset=["Year", "Sektor", "GovernancePillarScore", "AnnualReturnPct"])

        # Gruppierung und Mittelwertbildung je Jahr und Sektor
        df_grouped = (
            df_sector.groupby(["Year", "Sektor"])
            .agg({
                "GovernancePillarScore": "mean",
                "AnnualReturnPct": "mean"
            })
            .reset_index()
        )

        # Governance-Scores
        fig_score = px.line(
            df_grouped,
            x="Year",
            y="GovernancePillarScore",
            color="Sektor",
            title="Sektorale Entwicklung der Governance-Scores"
        )
        fig_score.update_layout(yaxis_title="Governance-Score", height=400)
        st.plotly_chart(fig_score, use_container_width=True)

        # Jahresrenditen
        fig_return = px.line(
            df_grouped,
            x="Year",
            y="AnnualReturnPct",
            color="Sektor",
            title="Sektorale Entwicklung der Jahresrenditen"
        )
        fig_return.update_layout(yaxis_title="Rendite (%)", height=400)
        st.plotly_chart(fig_return, use_container_width=True)