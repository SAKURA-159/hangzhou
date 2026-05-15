"""Reusable sidebar filter widget."""

import streamlit as st
import pandas as pd

import api_client as api


def render_sidebar() -> dict:
    """Render sidebar filters and return filter parameters dict for API calls."""
    st.sidebar.markdown("## 数据筛选")

    # Fetch all regions for multi-select
    stats = api.get_region_stats()
    all_regions = sorted(r["place"] for r in stats.get("regions", []))

    if not all_regions:
        all_regions = ["全部"]

    selected_regions = st.sidebar.multiselect(
        "选择区域",
        options=all_regions,
        default=all_regions[:5] if len(all_regions) > 5 else all_regions,
    )

    price_range = st.sidebar.slider(
        "价格范围 (元/㎡)",
        min_value=0,
        max_value=200000,
        value=(0, 100000),
        step=1000,
    )

    property_types = ["住宅", "别墅", "商业"]
    selected_types = st.sidebar.multiselect(
        "房产类型",
        options=property_types,
        default=property_types,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("## 数据概览")

    # Build filters dict for API
    filters: dict = {
        "page": 1,
        "page_size": 100,
        "price_min": price_range[0],
        "price_max": price_range[1],
        "property_type": selected_types[0] if len(selected_types) == 1 else None,
    }
    if selected_regions:
        filters["region"] = selected_regions[0] if len(selected_regions) == 1 else None
        # Store all selected regions for client-side filtering
        filters["_regions"] = selected_regions
    if selected_types:
        filters["_types"] = selected_types

    # Show overview stats
    overview = api.get_overview_stats(filters)
    total = overview.get("total_houses", 0)
    mean_price = overview.get("global_mean", 0)
    st.sidebar.metric("楼盘数", f"{total:,}")
    if total > 0:
        st.sidebar.metric("平均价格", f"{mean_price:,.0f} 元/㎡")
    else:
        st.sidebar.metric("平均价格", "—")

    return filters


def apply_client_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply client-side filters that aren't handled by the API."""
    if "_regions" in filters and filters["_regions"]:
        df = df[df["place"].isin(filters["_regions"])]
    if "_types" in filters and filters["_types"]:
        df = df[df["property_type"].isin(filters["_types"])]
    if "price_min" in filters:
        df = df[df["price"] >= filters["price_min"]]
    if "price_max" in filters:
        df = df[df["price"] <= filters["price_max"]]
    return df
