import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Berechnet annualisierte Normalrenditen in Prozent (AnnualReturnPct) aus monatlichen Prozentrenditen.
    Jahresrendite je (Company Name, Year): Produkt der Monatsfaktoren minus 1.
    """

    # Spaltennamen bereinigen
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    # Mindestanforderung prüfen
    required_cols = ["Company Name", "Date", "Close Price (USD)"]
    if not all(col in df.columns for col in required_cols):
        missing = [c for c in required_cols if c not in df.columns]
        raise KeyError(f"Fehlende Spalten: {', '.join(missing)}")

    # Datum konvertieren und Jahr ableiten
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Year"] = df["Date"].dt.year

    # Preise bereinigen
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    df = df[df["Close Price (USD)"] > 0]

    # Sortierung
    df = df.sort_values(by=["Company Name", "Date"])

    # Monatsrenditen als einfache Prozentänderungen
    df["MonthlyReturn"] = (
        df.groupby("Company Name")["Close Price (USD)"]
          .transform(lambda x: x.pct_change())
    )

    # Jahresrendite als verkettetes Produkt der Monatsrenditen; NaN, wenn keine Monatsrendite vorliegt
    annual = (
        df.groupby(["Company Name", "Year"])["MonthlyReturn"]
          .apply(lambda s: np.nan if s.dropna().shape[0] < 1 else (1 + s.dropna()).prod() - 1)
          .reset_index(name="AnnualReturn")
    )
    annual["AnnualReturnPct"] = annual["AnnualReturn"] * 100  # Prozent

    # Jahreskennzahl zurück in Monatsdaten mergen
    df = df.merge(
        annual[["Company Name", "Year", "AnnualReturnPct"]],
        on=["Company Name", "Year"],
        how="left"
    )

    return df
