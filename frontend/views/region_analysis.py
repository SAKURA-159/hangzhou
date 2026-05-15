"""区域分析 — compare price levels, distribution, and activity across regions."""

import pandas as pd
import streamlit as st

import api_client as api
from components.charts import (
    region_avg_price_bar,
    region_count_bar,
    region_median_bar,
    region_price_boxplot,
)
from components.dashboard import chart_card, footer, kpi_row, section_header
from components.filters import apply_client_filters, render_sidebar


def render() -> None:
    st.markdown("## 区域分析")
    st.caption("对比不同区域的价格水平、分布情况与热度。")

    filters = render_sidebar()

    resp = api.get_houses({**filters, "page": 1, "page_size": 5000})
    items = resp.get("items", [])
    if not items:
        st.warning("当前筛选条件下没有数据，请调整左侧筛选。")
        return

    df = pd.DataFrame(items)
    df = apply_client_filters(df, filters)

    if df.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    kpi_row(df)
    st.markdown("---")

    section_header("价格对比与分布", "各区域价格中位数排名与分布特征。")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**中位数排名**")
        chart_card(region_median_bar(df))
    with col2:
        st.markdown("**价格分布（箱线图）**")
        chart_card(region_price_boxplot(df))

    st.markdown("---")
    section_header("区域热度分析", "楼盘数量与均价排名。")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**楼盘数量（Top 10）**")
        chart_card(region_count_bar(df))
    with col4:
        st.markdown("**平均房价（Top 10）**")
        chart_card(region_avg_price_bar(df))

    footer()
