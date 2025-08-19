import math
import pandas as pd
import streamlit as st
import plotly.express as px
from scipy.stats import linregress

def governance_vs_rendite(df: pd.DataFrame):
    """
    Visualisiert den Zusammenhang zwischen ESG-Governance-Score und Jahresrendite
    – nach Unternehmen oder aggregiert nach Sektor.
    """

    st.subheader("Governance-Score im Vergleich zur Rendite")

    required = ["Company Name", "GovernancePillarScore", "AnnualReturnPct", "Year", "Sektor"]
    if not all(col in df.columns for col in required):
        st.error("Für diese Analyse fehlen eine oder mehrere Spalten.")
        return

    df = df.dropna(subset=required)
    df["AnnualReturnPct"] = pd.to_numeric(df["AnnualReturnPct"], errors="coerce")
    df = df[df["AnnualReturnPct"].between(-100, 100)]

    sektoren = sorted(df["Sektor"].dropna().unique())
    selected_sektoren = st.multiselect("Sektoren auswählen", sektoren, default=sektoren)
    if not selected_sektoren:
        st.warning("Bitte mindestens einen Sektor auswählen.")
        return
    df = df[df["Sektor"].isin(selected_sektoren)]

    modus = st.radio("Darstellungsmodus", ["Alle Unternehmen", "Sektordurchschnitte", "Einzelunternehmen"], horizontal=True)
    show_points = st.checkbox("Datenpunkte anzeigen", value=True)

    if modus == "Einzelunternehmen":
        companies = df["Company Name"].dropna().unique().tolist()
        all_selected = st.checkbox("Alle Unternehmen anzeigen", value=True)
        selected = companies if all_selected else st.multiselect("Unternehmen auswählen", companies, default=companies[:10])
        if not selected:
            st.warning("Bitte mindestens ein Unternehmen auswählen.")
            return
        df_filtered = df[df["Company Name"].isin(selected)]
        color_col = "Company Name"
        single_trend = False
    elif modus == "Sektordurchschnitte":
        df_filtered = (
            df.groupby(["Year", "Sektor"])
              .agg({"GovernancePillarScore": "mean", "AnnualReturnPct": "mean"})
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

    # Achendarstellung
    scale_all = st.checkbox("Alle Werte anzeigen", value=False)
    ret = pd.to_numeric(df_filtered["AnnualReturnPct"], errors="coerce").dropna()
    if ret.empty:
        y_min, y_max = -20.0, 20.0
    elif scale_all:
        y_min = math.floor(ret.min() / 5.0) * 5.0
        y_max = math.ceil(ret.max() / 5.0) * 5.0
        if y_max - y_min < 10.0:
            y_min -= 5.0
            y_max += 5.0
    else:
        q05 = float(ret.quantile(0.05))
        q95 = float(ret.quantile(0.95))
        R = max(10.0, 1.15 * max(abs(q05), abs(q95)))
        R = math.ceil(R / 5.0) * 5.0
        y_min, y_max = -R, R

    # Regressionskennzahlen aus gefilterten Daten
    x = pd.to_numeric(df_filtered["GovernancePillarScore"], errors="coerce")
    y = pd.to_numeric(df_filtered["AnnualReturnPct"], errors="coerce")
    mask = x.notna() & y.notna()
    if mask.sum() >= 2:
        slope, intercept, r_value, p_value, std_err = linregress(x[mask], y[mask])
    else:
        slope = r_value = p_value = float("nan")

    fig = px.scatter(
        df_filtered,
        x="GovernancePillarScore",
        y="AnnualReturnPct",
        color=color_col if not single_trend else None,
        trendline="ols",
        hover_data=df_filtered.columns,
        opacity=0.6 if show_points else 0.0,
        title=f"Governance-Score vs. Jahresrendite (r = {r_value:.2f}, Steigung {slope:.3f} %-Pkt/Scorepunkt)"
    )

    fig.add_hline(y=0, line_dash="dot", line_width=1)

    fig.update_layout(
        width=1000,
        height=600,
        xaxis_title="Governance-Score",
        yaxis_title="Rendite (%)",
        title_font=dict(size=20),
        xaxis=dict(title_font=dict(size=16), tickfont=dict(size=14)),
        yaxis=dict(title_font=dict(size=16), tickfont=dict(size=14),
                   range=[y_min, y_max], zeroline=True, ticksuffix=" %"),
        font=dict(family="Arial", size=14),
        margin=dict(l=60, r=30, t=60, b=60),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=True)

    stats = df_filtered["AnnualReturnPct"].agg(
        Mittelwert="mean", Median="median", StdAbw="std",
        Minimum="min", Maximum="max", N="count"
    ).round(2).to_frame().T
    stats.index = ["Jahresrendite (%)"]
    st.markdown("### Statistische Kennzahlen (Rendite)")
    st.dataframe(stats)

    st.markdown(f"**Korrelationskoeffizient:** {r_value:.2f}  ·  Steigung: {slope:.3f} %-Pkt je Scorepunkt  ·  p = {p_value:.3g}")
    if r_value > 0.2 and p_value < 0.05:
        st.info("Es liegt ein signifikanter positiver Zusammenhang zwischen Governance-Score und Jahresrendite vor.")
    elif r_value < -0.2 and p_value < 0.05:
        st.info("Es liegt ein signifikanter negativer Zusammenhang zwischen Governance-Score und Jahresrendite vor.")
    else:
        st.info("Es ist kein statistisch signifikanter Zusammenhang zwischen Governance-Score und Jahresrendite erkennbar.")

    if len(df_filtered) >= 20:
        st.markdown("---")
        st.markdown("### Verteilungen (Governance-Score & Rendite)")
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.histogram(df_filtered, x="GovernancePillarScore", nbins=40, title="Verteilung: Governance-Score")
            fig1.update_layout(xaxis_title="Governance-Score", yaxis_title="Häufigkeit", height=350,
                               xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)),
                               yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(df_filtered, x="AnnualReturnPct", nbins=50, title="Verteilung: Jahresrendite")
            fig2.update_layout(xaxis_title="Rendite (%)", yaxis_title="Häufigkeit", height=350,
                               xaxis=dict(title_font=dict(size=14), tickfont=dict(size=12), ticksuffix=" %"),
                               yaxis=dict(title_font=dict(size=14), tickfont=dict(size=12)))
            st.plotly_chart(fig2, use_container_width=True)