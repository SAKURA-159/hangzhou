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

    cards = [
        ("楼盘总数", f"{total:,}", "套"),
        ("平均价格", f"{avg_price:,.0f}", "元/㎡"),
        ("中位数价格", f"{median_price:,.0f}", "元/㎡"),
        ("覆盖区域", f"{regions}", "个"),
        ("平均面积", f"{avg_area:,.0f}" if avg_area > 0 else "—", "㎡" if avg_area > 0 else ""),
    ]

    html = '<div style="display:flex;gap:12px;margin-bottom:4px;">'
    for label, value, unit in cards:
        html += f"""<div style="flex:1;background:#fff;border-radius:10px;padding:16px 18px;
            border:1px solid #E0E5E5;text-align:center;min-width:0;">
            <p style="color:#7A8A8A;font-size:0.7rem;margin:0 0 6px 0;text-transform:uppercase;letter-spacing:0.04em;">{label}</p>
            <p style="color:#2D3A3A;font-size:1.3rem;font-weight:700;margin:0;">{value}<span style="font-size:0.75rem;font-weight:400;color:#9A9A9A;margin-left:3px;">{unit}</span></p>
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


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
