import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame, min_months_per_year: int = 12) -> pd.DataFrame:
    """
    AnnualReturnPct aus Monatsdaten (jeweils 01. des Monats):
    - Monatsrendite: pct_change je Unternehmen
    - Jahresrendite: geometrische Verknüpfung
    - Abdeckung: Jahreswert nur bei vollständigem Jahr
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    req = ["Company Name", "Date", "Close Price (USD)"]
    missing = [c for c in req if c not in df.columns]
    if missing:
        raise KeyError(f"Fehlende Spalten: {', '.join(missing)}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    df = df[df["Close Price (USD)"] > 0].sort_values(["Company Name", "Date"])

    # Eindeutigkeit je Monat sichern
    df["Month"] = df["Date"].dt.to_period("M")
    df = df.drop_duplicates(subset=["Company Name", "Month"], keep="first")

    # Monatsrenditen je Kalenderjahr
    df["Year"] = df["Date"].dt.year
    df["PeriodReturn"] = (
        df.groupby(["Company Name", "Year"], sort=False)["Close Price (USD)"].pct_change()
    )

    # Jahresaggregation mit konsistentem Guard
    def _annual_from_group(g: pd.DataFrame) -> float:
        n_months = g["Month"].nunique()
        s = g["PeriodReturn"].dropna()
        need_months = min_months_per_year
        need_returns = max(1, min_months_per_year - 1)
        if n_months < need_months or s.size < need_returns:
            return np.nan
        return (1.0 + s).prod() - 1.0

    annual = (
        df.groupby(["Company Name", "Year"], sort=False)
          .apply(_annual_from_group)
          .reset_index(name="AnnualReturn")
    )
    annual["AnnualReturnPct"] = annual["AnnualReturn"] * 100.0

    out = df.merge(
        annual[["Company Name", "Year", "AnnualReturnPct"]],
        on=["Company Name", "Year"], how="left"
    ).drop(columns=["PeriodReturn", "Month"])

    return out