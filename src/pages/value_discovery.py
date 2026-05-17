"""价值发现 — standalone version."""

import pandas as pd
import streamlit as st

from src.charts import value_discount_histogram, value_region_count_bar
from src.dashboard import chart_card, footer, section_header
from src.filters import render_sidebar
from src.data import get_filtered, COLUMN_LABELS


def render(df: pd.DataFrame) -> None:
    st.markdown("## 价值发现")
    st.markdown("### 价值楼盘发现")
    st.caption("寻找价格显著低于区域基准价（中位数/均值）的潜在价值楼盘")

    filters = render_sidebar(df)
    base = get_filtered(df, filters["regions"], filters["price_min"],
                        filters["price_max"], filters["property_types"])

    if "price" in base.columns:
        base["price"] = pd.to_numeric(base["price"], errors="coerce")
    base = base.dropna(subset=["place", "price"])
    base = base[base["price"] > 0]

    if base.empty:
        st.warning("当前筛选条件下无数据。")
        return

    c1, c2, c3 = st.columns([1.2, 1.2, 1.6])
    with c1:
        baseline = st.radio("基准价类型", options=["区域中位数", "区域均值"],
                            horizontal=True, index=0, key="tab3_baseline")
    with c2:
        discount_threshold = st.slider("折扣阈值 (%)", min_value=1, max_value=50,
                                       value=10, step=1, key="tab3_discount")
    with c3:
        min_region_count = st.number_input("忽略样本过少区域（最少楼盘数）",
                                           min_value=1, max_value=500, value=10, step=1,
                                           key="tab3_min_count")

    region_counts = base["place"].value_counts()
    keep_regions = region_counts[region_counts >= int(min_region_count)].index
    base = base[base["place"].isin(keep_regions)]

    if base.empty:
        st.warning("应用「最少楼盘数」过滤后无数据。")
        return

    if baseline == "区域中位数":
        region_base_price = base.groupby("place")["price"].median()
    else:
        region_base_price = base.groupby("place")["price"].mean()

    base["区域基准价"] = base["place"].map(region_base_price)
    base["折扣比例"] = (1 - base["price"] / base["区域基准价"]) * 100
    value_houses = base[base["折扣比例"] >= float(discount_threshold)].copy()

    if value_houses.empty:
        st.warning(f"未找到折扣 ≥ {discount_threshold}% 的价值楼盘。")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("价值楼盘数量", f"{len(value_houses):,}")
    k2.metric("覆盖区域数", f"{value_houses['place'].nunique():,}")
    k3.metric("平均折扣", f"{value_houses['折扣比例'].mean():.2f}%")
    k4.metric("最大折扣", f"{value_houses['折扣比例'].max():.2f}%")

    st.success(f"发现 {len(value_houses)} 个折扣 ≥ {discount_threshold}% 的价值楼盘（基准：{baseline}）")

    st.subheader("价值楼盘列表")
    display_columns = ["name", "place", "price", "区域基准价", "折扣比例"]
    for col in ["room_count", "avg_area", "property_type"]:
        if col in value_houses.columns:
            display_columns.append(col)

    sort_options = ["折扣比例", "price", "区域基准价", "place"]
    sort_labels = {v: COLUMN_LABELS.get(v, v) for v in sort_options}
    sort_by_label = st.selectbox(
        "排序方式",
        options=[sort_labels[v] for v in sort_options],
        index=0,
        key="tab3_sort",
    )
    label_to_sort = {sort_labels[v]: v for v in sort_options}
    sort_by = label_to_sort[sort_by_label]
    sort_ascending = st.checkbox("升序排序", value=(sort_by != "折扣比例"), key="tab3_asc")

    value_houses_display = value_houses.sort_values(sort_by, ascending=sort_ascending)
    page_size = st.selectbox("每页显示数量", [10, 20, 50, 100], index=0, key="tab3_ps")
    total_rows = len(value_houses_display)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    page_number = st.number_input("页码", min_value=1, max_value=total_pages,
                                  value=1, step=1, key="tab3_pn")

    start_idx = (int(page_number) - 1) * int(page_size)
    end_idx = min(start_idx + int(page_size), total_rows)
    show_df = value_houses_display.iloc[start_idx:end_idx][display_columns].copy()
    for c in ["price", "区域基准价"]:
        if c in show_df.columns:
            show_df[c] = pd.to_numeric(show_df[c], errors="coerce").round(0).astype(str).replace("nan", "—")
    if "折扣比例" in show_df.columns:
        show_df["折扣比例"] = pd.to_numeric(show_df["折扣比例"], errors="coerce").round(2).astype(str).replace("nan", "—") + "%"

    display_df = show_df.fillna("—").astype(str)
    display_df = display_df.rename(columns=lambda c: COLUMN_LABELS.get(c, c))
    st.dataframe(display_df, use_container_width=True, height=420)
    st.caption(f"显示第 {start_idx + 1} - {end_idx} 条，共 {total_rows} 条；第 {page_number}/{total_pages} 页")

    csv = value_houses_display[display_columns].to_csv(index=False).encode("utf-8-sig")
    st.download_button("下载价值楼盘数据 (CSV)", data=csv,
                       file_name=f"杭州价值楼盘_折扣≥{discount_threshold}%_{baseline}.csv",
                       mime="text/csv", key="tab3_dl")

    st.markdown("---")
    section_header("价值楼盘区域分布", "价值楼盘的集中区域与折扣分布形态。")
    colA, colB = st.columns(2)
    with colA:
        chart_card(value_region_count_bar(value_houses))
    with colB:
        chart_card(value_discount_histogram(value_houses))

    footer()
