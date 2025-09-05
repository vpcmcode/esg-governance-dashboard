import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame, min_months_per_year: int = 12) -> pd.DataFrame:
    """
    AnnualReturnPct aus Monatsdaten (jeweils 01. des Monats):
    - Monatsrendite: pct_change je Unternehmen
    - Jahresrendite: geometrische Verknüpfung; nur bei ausreichender Abdeckung
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    req = ["Company Name", "Date", "Close Price (USD)"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise KeyError(f"Fehlende Spalten: {', '.join(missing)}")

    # Typisierung
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    df = df[df["Close Price (USD)"] > 0].sort_values(["Company Name", "Date"])

    # Eindeutigkeit auf Monatsebene
    df["Month"] = df["Date"].dt.to_period("M")
    df = df.drop_duplicates(subset=["Company Name", "Month"], keep="first")

    # Monatsrendite auf Basis der verfügbaren Daten
    df["PeriodReturn"] = df.groupby("Company Name", sort=False)["Close Price (USD)"].pct_change()

    # Jahresaggregation
    df["Year"] = df["Date"].dt.year
    counts = df.groupby(["Company Name", "Year"])["Month"].nunique()

    def geo_annual(s: pd.Series, n_obs: int) -> float:
        s = s.dropna()
        if n_obs < min_months_per_year or s.size < min_months_per_year:
            return np.nan
        return (1.0 + s).prod() - 1.0

    annual = (
        df.groupby(["Company Name", "Year"], sort=False)
          .apply(lambda g: geo_annual(g["PeriodReturn"], n_obs=counts.loc[(g.name[0], g.name[1])]))
          .reset_index(name="AnnualReturn")
    )
    annual["AnnualReturnPct"] = annual["AnnualReturn"] * 100.0

    # Merge in den Datensatz
    out = df.merge(annual[["Company Name", "Year", "AnnualReturnPct"]],
                   on=["Company Name", "Year"], how="left") \
            .drop(columns=["PeriodReturn", "Month"])

    return out