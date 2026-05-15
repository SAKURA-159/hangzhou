"""价值发现 page — find houses below regional baseline prices."""

import pandas as pd
import streamlit as st

import api_client as api
from components.charts import value_discount_histogram, value_region_count_bar
from components.dashboard import chart_card, footer, section_header
from components.filters import apply_client_filters, render_sidebar


def render() -> None:
    st.markdown("## 价值发现")
    st.markdown("### 价值楼盘发现")
    st.caption("寻找价格显著低于区域基准价（中位数/均值）的潜在价值楼盘")

    filters = render_sidebar()

    resp = api.get_houses({**filters, "page": 1, "page_size": 5000})
    items = resp.get("items", [])
    if not items:
        st.warning("当前筛选条件下无数据。")
        return

    base = pd.DataFrame(items)
    base = apply_client_filters(base, filters)

    if "price" in base.columns:
        base["price"] = pd.to_numeric(base["price"], errors="coerce")
    base = base.dropna(subset=["place", "price"])
    base = base[base["price"] > 0]

    if base.empty:
        st.warning("当前筛选条件下无数据。")
        return

    c1, c2, c3 = st.columns([1.2, 1.2, 1.6])

    with c1:
        baseline = st.radio(
            "基准价类型",
            options=["区域中位数", "区域均值"],
            horizontal=True,
            index=0,
            key="tab3_baseline",
        )

    with c2:
        discount_threshold = st.slider(
            "折扣阈值 (%)",
            min_value=1,
            max_value=50,
            value=10,
            step=1,
            help="例如 10%：表示楼盘单价低于区域基准价的 90% 才会被识别为价值盘",
            key="tab3_discount_threshold",
        )

    with c3:
        min_region_count = st.number_input(
            "忽略样本过少区域（最少楼盘数）",
            min_value=1,
            max_value=500,
            value=10,
            step=1,
            help="某区域样本太少会导致基准价不稳定，建议设一个下限",
            key="tab3_min_region_count",
        )

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)

    region_counts = base["place"].value_counts()
    keep_regions = region_counts[region_counts >= int(min_region_count)].index
    base = base[base["place"].isin(keep_regions)]

    if base.empty:
        st.warning("应用『最少楼盘数』过滤后无数据。请降低阈值或放宽筛选条件。")
        return

    if baseline == "区域中位数":
        region_base_price = base.groupby("place")["price"].median()
    else:
        region_base_price = base.groupby("place")["price"].mean()

    base["区域基准价"] = base["place"].map(region_base_price)
    base["折扣比例"] = (1 - base["price"] / base["区域基准价"]) * 100
    value_houses = base[base["折扣比例"] >= float(discount_threshold)].copy()

    if value_houses.empty:
        st.warning(f"在当前筛选条件下，未找到折扣 ≥ {discount_threshold}% 的价值楼盘。")
        st.info("建议：降低折扣阈值、放宽价格范围或减少『最少楼盘数』限制。")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("价值楼盘数量", f"{len(value_houses):,}")
    k2.metric("覆盖区域数", f"{value_houses['place'].nunique():,}")
    k3.metric("平均折扣", f"{value_houses['折扣比例'].mean():.2f}%")
    k4.metric("最大折扣", f"{value_houses['折扣比例'].max():.2f}%")

    st.success(f"发现 {len(value_houses)} 个折扣 ≥ {discount_threshold}% 的价值楼盘（基准：{baseline}）")

    st.subheader("价值楼盘列表")

    display_columns = ["name", "place", "price", "区域基准价", "折扣比例"]
    if "room_count" in value_houses.columns:
        display_columns.append("room_count")
    if "avg_area" in value_houses.columns:
        display_columns.append("avg_area")
    if "property_type" in value_houses.columns:
        display_columns.append("property_type")

    sort_by = st.selectbox(
        "排序方式",
        options=["折扣比例", "price", "区域基准价", "place"],
        index=0,
        key="tab3_sort_by",
    )

    default_ascending = False if sort_by == "折扣比例" else True
    sort_ascending = st.checkbox("升序排序", value=default_ascending, key="tab3_sort_ascending")

    value_houses_display = value_houses.sort_values(sort_by, ascending=sort_ascending)

    page_size = st.selectbox("每页显示数量", [10, 20, 50, 100], index=0, key="tab3_page_size")
    total_rows = len(value_houses_display)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)

    page_number = st.number_input(
        "页码", min_value=1, max_value=total_pages, value=1, step=1, key="tab3_page_number",
    )

    start_idx = (int(page_number) - 1) * int(page_size)
    end_idx = min(start_idx + int(page_size), total_rows)

    show_df = value_houses_display.iloc[start_idx:end_idx][display_columns].copy()
    for col in ["price", "区域基准价"]:
        if col in show_df.columns:
            show_df[col] = pd.to_numeric(show_df[col], errors="coerce").round(0)
    if "折扣比例" in show_df.columns:
        show_df["折扣比例"] = pd.to_numeric(show_df["折扣比例"], errors="coerce").round(2)

    st.dataframe(show_df.fillna("—"), use_container_width=True, height=420)
    st.caption(f"显示第 {start_idx + 1} - {end_idx} 条，共 {total_rows} 条；第 {page_number}/{total_pages} 页")

    # CSV download
    csv = value_houses_display[display_columns].to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="下载价值楼盘数据 (CSV)",
        data=csv,
        file_name=f"杭州价值楼盘_折扣≥{discount_threshold}%_{baseline}.csv",
        mime="text/csv",
        key="tab3_download_csv",
    )

    st.markdown("---")
    section_header("价值楼盘区域分布", "价值楼盘的集中区域与折扣分布形态。")
    colA, colB = st.columns(2)

    with colA:
        chart_card(value_region_count_bar(value_houses))

    with colB:
        chart_card(value_discount_histogram(value_houses))

    footer()
