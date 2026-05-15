"""价格分析 — standalone version."""

import pandas as pd
import streamlit as st

from src.charts import area_price_correlation, price_histogram, price_vs_area_scatter, property_type_boxplot
from src.dashboard import chart_card, footer, kpi_row, section_header
from src.filters import render_sidebar
from src.data import get_filtered


def render(df: pd.DataFrame) -> None:
    st.markdown("## 价格分析")
    st.caption("房价分布特征、不同房产类型价格对比、面积与价格关系。")

    filters = render_sidebar(df)
    filtered = get_filtered(df, filters["regions"], filters["price_min"],
                            filters["price_max"], filters["property_types"])

    if filtered.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    kpi_row(filtered)
    st.markdown("---")

    section_header("价格分布", "房价整体分布特征与离散情况。")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**价格分布直方图**")
        if "price" in filtered.columns:
            chart_card(price_histogram(filtered))
        else:
            st.info("缺少价格字段。")

    with col2:
        st.markdown("**房产类型价格对比**")
        if "property_type" in filtered.columns and "price" in filtered.columns:
            chart_card(property_type_boxplot(filtered))
        else:
            st.info("缺少房产类型或价格字段。")

    st.markdown("---")
    section_header("面积与价格", "探索房屋面积与单价之间的关联。")
    if "avg_area" in filtered.columns and "price" in filtered.columns:
        area_df = filtered.dropna(subset=["avg_area", "price"])
        if not area_df.empty:
            col_a, col_b = st.columns([3, 1])
            with col_a:
                chart_card(price_vs_area_scatter(filtered))
            with col_b:
                if len(area_df) > 1:
                    corr = area_price_correlation(filtered)
                    st.metric("面积与价格相关性", f"{corr:.3f}")
                    st.metric("平均面积", f"{area_df['avg_area'].mean():.0f} ㎡")
                    st.metric("面积中位数", f"{area_df['avg_area'].median():.0f} ㎡")
        else:
            st.info("缺少有效面积数据。")
    else:
        st.info("缺少面积或价格字段。")

    footer()
