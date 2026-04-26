"""Booth data merging and progress functions."""
import pandas as pd


def merge_booth_data(live_df: pd.DataFrame, historical_df: pd.DataFrame) -> pd.DataFrame:
    """Merge live and historical booth data on booth_id."""
    if live_df.empty:
        return pd.DataFrame()
    if historical_df.empty:
        return live_df.copy()
    merged = live_df.merge(historical_df, on="booth_id", how="left", suffixes=("", "_hist"))
    return merged


def calculate_booth_progress(live_df: pd.DataFrame) -> pd.DataFrame:
    """Add a counted_pct column to the booth dataframe."""
    if live_df.empty:
        return live_df
    df = live_df.copy()
    primary_cols = [c for c in df.columns if c.endswith("_primary")]
    if primary_cols:
        df["total_primary_counted"] = df[primary_cols].sum(axis=1)
        if "total_enrolled" in df.columns:
            df["counted_pct"] = (df["total_primary_counted"] / df["total_enrolled"].replace(0, 1)) * 100
        else:
            df["counted_pct"] = 0.0
    else:
        df["total_primary_counted"] = 0
        df["counted_pct"] = 0.0
    return df
