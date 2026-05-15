"""价格分析 page — price distribution, property type comparison, price vs area."""

import pandas as pd
import streamlit as st

import api_client as api
from components.charts import (
    area_price_correlation,
    price_histogram,
    price_vs_area_scatter,
    property_type_boxplot,
)
from components.dashboard import chart_card, footer, kpi_row, section_header
from components.filters import apply_client_filters, render_sidebar


def render() -> None:
    st.markdown("## 价格分析")
    st.caption("房价分布特征、不同房产类型价格对比、面积与价格关系。")

    filters = render_sidebar()

    resp = api.get_houses({**filters, "page": 1, "page_size": 5000})
    items = resp.get("items", [])
    if not items:
        st.warning("当前筛选条件下没有数据。")
        return

    df = pd.DataFrame(items)
    df = apply_client_filters(df, filters)

    if df.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    kpi_row(df)
    st.markdown("---")

    section_header("价格分布", "房价整体分布特征与离散情况。")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**价格分布直方图**")
        if "price" in df.columns:
            chart_card(price_histogram(df))
        else:
            st.info("缺少价格字段。")

    with col2:
        st.markdown("**房产类型价格对比**")
        if "property_type" in df.columns and "price" in df.columns:
            chart_card(property_type_boxplot(df))
        else:
            st.info("缺少房产类型或价格字段。")

    st.markdown("---")
    section_header("面积与价格", "探索房屋面积与单价之间的关联。")
    if "avg_area" in df.columns and "price" in df.columns:
        area_df = df.dropna(subset=["avg_area", "price"])
        if not area_df.empty:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                chart_card(price_vs_area_scatter(df))
            with col_b:
                if len(area_df) > 1:
                    corr = area_price_correlation(df)
                    st.metric("面积与价格相关性", f"{corr:.3f}")
                    # Extra contextual metrics
                    st.metric("平均面积", f"{area_df['avg_area'].mean():.0f} ㎡")
                    st.metric("面积中位数", f"{area_df['avg_area'].median():.0f} ㎡")
        else:
            st.info("缺少有效面积数据。")
    else:
        st.info("缺少面积或价格字段。")

    footer()
