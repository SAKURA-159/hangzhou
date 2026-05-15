"""Sidebar filter widget — standalone version using local DataFrame."""

import pandas as pd
import streamlit as st

from src.data import get_all_regions


def render_sidebar(df: pd.DataFrame) -> dict:
    """Render sidebar filters and return filter parameters dict."""
    st.sidebar.markdown("## 数据筛选")

    all_regions = get_all_regions(df)
    selected_regions = st.sidebar.multiselect(
        "选择区域", options=all_regions,
        default=all_regions[:5] if len(all_regions) > 5 else all_regions,
    )

    price_min_val = int(df["price"].min()) if "price" in df.columns else 0
    price_max_val = int(df["price"].max()) if "price" in df.columns else 200000
    price_range = st.sidebar.slider(
        "价格范围 (元/㎡)", min_value=price_min_val, max_value=price_max_val,
        value=(price_min_val, min(price_max_val, 100000)),
    )

    property_types = ["住宅", "别墅", "商业"]
    selected_types = st.sidebar.multiselect(
        "房产类型", options=property_types, default=property_types,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 数据概览")

    filtered = df.copy()
    if selected_regions:
        filtered = filtered[filtered["place"].isin(selected_regions)]
    if selected_types:
        filtered = filtered[filtered["property_type"].isin(selected_types)]
    filtered = filtered[
        (filtered["price"] >= price_range[0]) & (filtered["price"] <= price_range[1])
    ]

    st.sidebar.metric("楼盘数", f"{len(filtered):,}")
    if len(filtered) > 0:
        st.sidebar.metric("平均价格", f"{filtered['price'].mean():,.0f} 元/㎡")
    else:
        st.sidebar.metric("平均价格", "—")
    st.sidebar.caption(f"全库共 {len(df):,} 条")

    return {
        "regions": selected_regions,
        "price_min": price_range[0],
        "price_max": price_range[1],
        "property_types": selected_types,
    }
