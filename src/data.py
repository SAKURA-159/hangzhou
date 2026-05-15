"""Local CSV data loader — standalone version (no backend API needed)."""

from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load housing data from CSV, with encoding auto-detection."""
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"

    cleaned_path = data_dir / "hangzhou_house_cleaned.csv"
    raw_path = data_dir / "hangzhouhouseprice.csv"

    if cleaned_path.exists():
        path = cleaned_path
    elif raw_path.exists():
        path = raw_path
    else:
        st.error(f"数据文件未找到: {cleaned_path} 或 {raw_path}")
        return pd.DataFrame()

    for enc in ["utf-8-sig", "gbk", "gb18030"]:
        try:
            df = pd.read_csv(path, encoding=enc)
            break
        except UnicodeDecodeError:
            continue

    # Normalize column names
    col_map = {
        "House name": "name", "House place": "place", "House price": "price",
        "House introduction": "introduction", "room_count": "room_count",
        "min_area": "min_area", "max_area": "max_area", "avg_area": "avg_area",
        "property_type": "property_type", "price_flag": "price_flag",
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})
    df = df.drop_duplicates()

    # Clean numeric columns
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        df = df.dropna(subset=["price"])
    if "introduction" in df.columns:
        df["introduction"] = df["introduction"].fillna("—")
    for col in ("room_count", "min_area", "max_area", "avg_area"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def get_filtered(df: pd.DataFrame, regions=None, price_min=None, price_max=None,
                 property_types=None) -> pd.DataFrame:
    """Apply filters to DataFrame (client-side)."""
    result = df.copy()
    if regions:
        result = result[result["place"].isin(regions)]
    if price_min is not None:
        result = result[result["price"] >= price_min]
    if price_max is not None:
        result = result[result["price"] <= price_max]
    if property_types:
        result = result[result["property_type"].isin(property_types)]
    return result


def get_all_regions(df: pd.DataFrame) -> list[str]:
    return sorted(df["place"].dropna().unique().tolist())
