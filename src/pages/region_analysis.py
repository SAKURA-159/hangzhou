"""区域分析 — standalone version."""

import pandas as pd
import streamlit as st

from src.charts import region_avg_price_bar, region_count_bar, region_median_bar, region_price_boxplot
from src.dashboard import chart_card, footer, kpi_row, section_header
from src.filters import render_sidebar
from src.data import get_filtered


def render(df: pd.DataFrame) -> None:
    st.markdown("## 区域分析")
    st.caption("对比不同区域的价格水平、分布情况与热度。")

    filters = render_sidebar(df)
    filtered = get_filtered(df, filters["regions"], filters["price_min"],
                            filters["price_max"], filters["property_types"])

    if filtered.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    kpi_row(filtered)
    st.markdown("---")

    section_header("价格对比与分布", "各区域价格中位数排名与分布特征。")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**中位数排名**")
        chart_card(region_median_bar(filtered))
    with col2:
        st.markdown("**价格分布（箱线图）**")
        chart_card(region_price_boxplot(filtered))

    st.markdown("---")
    section_header("区域热度分析", "楼盘数量与均价排名。")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**楼盘数量（Top 10）**")
        chart_card(region_count_bar(filtered))
    with col4:
        st.markdown("**平均房价（Top 10）**")
        chart_card(region_avg_price_bar(filtered))

    footer()
