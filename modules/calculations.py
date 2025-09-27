import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame,
                      min_months_per_year: int = 12,
                      partial_policy: str = "strict",
                      min_months_for_partial: int = 6) -> pd.DataFrame:
    """
    Berechnet annualisierte Renditen pro Unternehmen und Jahr basierend auf Monatsdaten.
    """
    df = df.copy()
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    # Pflichtspalten prüfen
    required_cols = ["Company Name", "Date", "Close Price (USD)"]
    if any(col not in df.columns for col in required_cols):
        raise KeyError("Fehlende Pflichtspalten für die Renditeberechnung.")

    # Typkonvertierung und Sortierung
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    df = df[df["Close Price (USD)"] > 0].sort_values(["Company Name", "Date"])

    # Monatliche Eindeutigkeit
    df["Month"] = df["Date"].dt.to_period("M")
    df = df.drop_duplicates(subset=["Company Name", "Month"])

    # Jahreszuordnung und monatliche Renditen
    df["Year"] = df["Date"].dt.year
    df["PeriodReturn"] = df.groupby(["Company Name", "Year"])["Close Price (USD)"].pct_change()

    # Jahresrenditen je nach Aggregationsstrategie berechnen
    def _aggregate_annual(group: pd.DataFrame) -> float:
        returns = group["PeriodReturn"].dropna()
        months = group["Month"].sort_values().unique()
        n_months = len(months)
        n_returns = len(returns)
        full_year = (n_months >= min_months_per_year) and (n_returns >= max(1, min_months_per_year - 1))
        factor = (1.0 + returns).prod() if n_returns > 0 else np.nan

        if partial_policy == "strict":
            return factor - 1.0 if full_year else np.nan

        elif partial_policy == "ytd_partial":
            if full_year:
                return factor - 1.0
            if n_months < min_months_for_partial or n_returns < 1:
                return np.nan
            return factor - 1.0

        elif partial_policy == "annualize_by_span":
            if full_year:
                return factor - 1.0
            if n_months < min_months_for_partial or n_returns < 1:
                return np.nan
            m0, m1 = months[0], months[-1]
            months_span = (m1.year - m0.year) * 12 + (m1.month - m0.month)
            if months_span <= 0:
                return np.nan
            monthly_factor = factor ** (1.0 / months_span)
            return monthly_factor ** 12 - 1.0

        else:
            raise ValueError("Ungültiger Wert für partial_policy.")

    annual = (
        df.groupby(["Company Name", "Year"])
          .apply(_aggregate_annual)
          .reset_index(name="AnnualReturn")
    )
    annual["AnnualReturnPct"] = annual["AnnualReturn"] * 100.0

    # Zusammenführen und Aufbereitung
    out = df.merge(annual, on=["Company Name", "Year"], how="left")
    out.drop(columns=["PeriodReturn", "Month"], inplace=True)

    return out