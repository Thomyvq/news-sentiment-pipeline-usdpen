from pathlib import Path
import pandas as pd
import yfinance as yf

def fetch_usdpen_yahoo(start_date: str, end_date: str, out_path="data/market/usdpen_yahoo.csv") -> pd.DataFrame:
    """
    Descarga USD/PEN (ticker: PEN=X) desde Yahoo Finance.
    Retorna DataFrame con date, open, high, low, close, volume.
    """
    df = yf.download("PEN=X", start=start_date, end=end_date, interval="1d", auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise RuntimeError("Yahoo no devolvió datos para PEN=X en el rango dado.")

    df = df.reset_index()

    # Normalizar columnas
    rename_map = {
        "Date": "date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    }
    df = df.rename(columns=rename_map)

    # Asegurar tipo fecha (solo día)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"✔ FX guardado: {out_path} ({len(df)} filas)")

    return df
