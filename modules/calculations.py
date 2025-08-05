import pandas as pd
import numpy as np

def calculate_log_returns(df: pd.DataFrame) -> pd.DataFrame:
    # Spaltennamen bereinigen
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    # Mindestanforderung
    required_cols = ["Company Name", "Date", "Close Price (USD)"]
    if not all(col in df.columns for col in required_cols):
        missing = [c for c in required_cols if c not in df.columns]
        raise KeyError(f"Fehlende Spalten: {', '.join(missing)}")

    # Datum konvertieren und Jahresvariable erzeugen
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df["Year"] = df["Date"].dt.year

    # Preisspalte bereinigen
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    before_clean = len(df)
    df = df[df["Close Price (USD)"] > 0]
    after_clean = len(df)

    # Sortierung innerhalb der Unternehmen nach Zeitverlauf
    df = df.sort_values(by=["Company Name", "Date"])

    # Monatsrenditen
    df["MonthlyLogReturn"] = (
        df.groupby("Company Name")["Close Price (USD)"]
          .transform(lambda x: np.log(x / x.shift(1)))
    )
    # Annualisierung der Monatsrenditen je Kalenderjahr
    annual_log = (
        df.groupby(["Company Name", "Year"])["MonthlyLogReturn"]
          .sum()
          .reset_index()
          .rename(columns={"MonthlyLogReturn": "AnnualLogReturn"})
    )

    # Umwandlung in prozentuale Rendite
    annual_log["AnnualReturnPct"] = (np.exp(annual_log["AnnualLogReturn"]) - 1) * 100

    # jährliche Kennzahlen zurück in Monatsdaten mergen
    df = df.merge(annual_log, on=["Company Name", "Year"], how="left")
    df["LogReturn"] = df["AnnualReturnPct"]

    # Konsole/Debugging
    valid_obs = annual_log.dropna().shape[0]
    companies = annual_log["Company Name"].nunique()
    print(f"Renditen berechnet für {valid_obs} Unternehmensjahre ({companies} Unternehmen).")
    print(f"{before_clean - after_clean} Zeilen mit ungültigen Preisen entfernt.")

    return df