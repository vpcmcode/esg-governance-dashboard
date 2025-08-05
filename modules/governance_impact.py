import pandas as pd
import streamlit as st
import plotly.express as px

def governance_vs_rendite(df: pd.DataFrame):
    """
    Visualisiert den Zusammenhang zwischen ESG-Governance-Score und Jahresrendite
    – nach Unternehmen oder aggregiert nach Sektor.
    """

    st.subheader("Governance-Score im Vergleich zur Rendite")

    # Sicherstellen, dass alle nötigen Spalten vorhanden sind
    required = ["Company Name", "GovernancePillarScore", "AnnualReturnPct", "Year", "Sektor"]
    if not all(col in df.columns for col in required):
        st.error("Für diese Analyse fehlen eine oder mehrere Spalten.")
        return

    # Bereinigung: NaNs entfernen, Renditen validieren
    df = df.dropna(subset=required)
    df["AnnualReturnPct"] = pd.to_numeric(df["AnnualReturnPct"], errors="coerce")
    df = df[df["AnnualReturnPct"].between(-100, 100)]

    # Sektorfilterung
    sektoren = sorted(df["Sektor"].dropna().unique())
    selected_sektoren = st.multiselect("Sektoren auswählen", sektoren, default=sektoren)

    if not selected_sektoren:
        st.warning("Bitte mindestens einen Sektor auswählen.")
        return

    df = df[df["Sektor"].isin(selected_sektoren)]

    # Darstellungsauswahl
    modus = st.radio("Darstellungsmodus", ["Alle Unternehmen", "Sektordurchschnitte", "Einzelunternehmen"], horizontal=True)
    show_points = st.checkbox("Datenpunkte anzeigen", value=False)

    if modus == "Einzelunternehmen":
        companies = df["Company Name"].dropna().unique().tolist()
        all_selected = st.checkbox("Alle Unternehmen anzeigen", value=True)
        if all_selected:
            selected = companies
        else:
            selected = st.multiselect("Unternehmen auswählen", companies, default=companies[:10])
        if not selected:
            st.warning("Bitte mindestens ein Unternehmen auswählen.")
            return
        df_filtered = df[df["Company Name"].isin(selected)]
        color_col = "Company Name"
        single_trend = False

    elif modus == "Sektordurchschnitte":
        df_filtered = (
            df.groupby(["Year", "Sektor"])
            .agg({
                "GovernancePillarScore": "mean",
                "AnnualReturnPct": "mean"
            })
            .reset_index()
        )
        color_col = "Sektor"
        single_trend = False

    else:
        df_filtered = df.copy()
        color_col = None
        single_trend = True

    if df_filtered.empty:
        st.warning("Keine Daten für die aktuelle Auswahl.")
        return

    # Streudiagramm Governance vs. Rendite
    fig = px.scatter(
        df_filtered,
        x="GovernancePillarScore",
        y="AnnualReturnPct",
        color=color_col if not single_trend else None,
        trendline="ols",
        hover_data=df_filtered.columns,
        opacity=0.7 if show_points else 0,
        title="Governance-Score vs. Jahresrendite"
    )
    fig.update_layout(
        height=600,
        xaxis_title="Governance-Score",
        yaxis_title="Rendite (%)"
    )
    fig.update_yaxes(range=[-100, 100])
    st.plotly_chart(fig, use_container_width=True)

    # Statistische Auswertung der aktuellen Auswahl
    stats = df_filtered["AnnualReturnPct"].agg(
        Mittelwert="mean",
        Median="median",
        StdAbw="std",
        Minimum="min",
        Maximum="max",
        N="count"
    ).round(2).to_frame().T

    st.markdown("### Statistische Kennzahlen (Rendite)")
    st.dataframe(stats)

    # Einfache Interpretation auf Basis der Korrelation
    correlation = df_filtered["GovernancePillarScore"].corr(df_filtered["AnnualReturnPct"])
    st.markdown(f"**Korrelationskoeffizient:** {correlation:.2f}")
    if correlation > 0.2:
        st.info("↗ Höhere Governance-Scores gehen tendenziell mit besseren Renditen einher.")
    elif correlation < -0.2:
        st.info("↘ Höhere Governance-Scores korrelieren tendenziell mit geringeren Renditen.")
    else:
        st.info("➖ Kein klarer Zusammenhang zwischen Score und Rendite.")

    # Histogrammverteilung nur bei ausreichender Fallzahl
    if len(df_filtered) >= 20:
        st.markdown("---")
        st.markdown("### Verteilungen (Governance-Score & Rendite)")

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.histogram(
                df_filtered,
                x="GovernancePillarScore",
                nbins=40,
                title="Verteilung: Governance-Score"
            )
            fig1.update_layout(xaxis_title="Governance-Score", yaxis_title="Häufigkeit", height=350)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(
                df_filtered,
                x="AnnualReturnPct",
                nbins=50,
                title="Verteilung: Jahresrendite"
            )
            fig2.update_layout(xaxis_title="Rendite (%)", yaxis_title="Häufigkeit", height=350)
            st.plotly_chart(fig2, use_container_width=True)