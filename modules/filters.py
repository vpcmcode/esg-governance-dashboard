import pandas as pd

def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtert und bereinigt das ESG-Governance-Dataset für die weitere Analyse.
    """

    # Datenbereinigung
    df.columns = [col.strip().replace('\ufeff', '') for col in df.columns]

    # Erwartete Pflichtspalten
    required_columns = ["Company Name", "GovernancePillarScore", "Close Price (USD)", "Date"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Fehlende Spalten im Datensatz: {', '.join(missing_columns)}")

    # Konvertiert das Datumsfeld und filtert unbrauchbare Zeilen
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df[df["Date"].notna()]
    df["Year"] = df["Date"].dt.year

    # Wandelt numerische Felder explizit um
    df["Close Price (USD)"] = pd.to_numeric(df["Close Price (USD)"], errors="coerce")
    df["GovernancePillarScore"] = pd.to_numeric(df["GovernancePillarScore"], errors="coerce")

    # Sektorbereinigung
    if "Sector" in df.columns:
        df["Sector"] = df["Sector"].astype(str).str.strip()

    # Entfernt Zeilen mit fehlenden Kerndaten
    df = df[
        df["Company Name"].notna() &
        df["GovernancePillarScore"].notna() &
        df["Close Price (USD)"].notna() &
        df["Year"].notna()
    ]

    return df