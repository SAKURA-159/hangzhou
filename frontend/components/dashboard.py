"""Shared dashboard UI components — KPI cards, section wrappers, footer."""

import pandas as pd
import streamlit as st


def kpi_row(df: pd.DataFrame) -> None:
    """Show a row of key metrics at the top of each page."""
    if df.empty:
        return

    total = len(df)
    avg_price = df["price"].mean() if "price" in df.columns else 0
    median_price = df["price"].median() if "price" in df.columns else 0
    regions = df["place"].nunique() if "place" in df.columns else 0
    avg_area = df["avg_area"].mean() if "avg_area" in df.columns else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("当前楼盘数", f"{total:,}")
    col2.metric("均价", f"{avg_price:,.0f} 元/㎡")
    col3.metric("中位数价格", f"{median_price:,.0f} 元/㎡")
    col4.metric("覆盖区域", f"{regions}")
    col5.metric("平均面积", f"{avg_area:,.0f} ㎡" if avg_area > 0 else "—")


def section_header(title: str, description: str = "") -> None:
    """Consistent section header with optional description."""
    st.markdown(f"### {title}")
    if description:
        st.caption(description)


def chart_card(fig, use_container_width: bool = True):
    """Wrapper — charts are already styled by beautify_plotly."""
    st.plotly_chart(fig, use_container_width=use_container_width, config={"displayModeBar": False})


def footer() -> None:
    """Dashboard footer."""
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#9A9A9A;font-size:0.78rem;padding-bottom:1rem;'>
        杭州房地产市场分析 · 数据来源公开信息 · 仅供参考
    </div>
    """, unsafe_allow_html=True)
