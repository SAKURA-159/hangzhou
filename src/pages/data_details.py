"""数据详情 — standalone version."""

import pandas as pd
import streamlit as st

from src.dashboard import footer, kpi_row, section_header
from src.filters import render_sidebar
from src.data import get_filtered, COLUMN_LABELS


def render(df: pd.DataFrame) -> None:
    st.header("详细数据浏览")

    filters = render_sidebar(df)
    filtered = get_filtered(df, filters["regions"], filters["price_min"],
                            filters["price_max"], filters["property_types"])

    if filtered.empty:
        st.warning("当前筛选条件下没有数据。")
        return

    kpi_row(filtered)
    st.markdown("---")

    section_header("数据浏览", "查看和导出当前筛选条件下的房源数据。")

    all_columns = list(filtered.columns)
    col_labels = {c: COLUMN_LABELS.get(c, c) for c in all_columns}
    default_columns = ["name", "place", "price", "property_type"]
    for c in ["room_count", "avg_area"]:
        if c in all_columns:
            default_columns.append(c)

    selected_labels = st.multiselect(
        "选择显示的列",
        options=[col_labels[c] for c in all_columns],
        default=[col_labels[c] for c in default_columns if c in all_columns],
    )
    if not selected_labels:
        return
    label_to_col = {v: k for k, v in col_labels.items()}
    selected_columns = [label_to_col[l] for l in selected_labels]

    sort_column_label = st.selectbox(
        "排序依据",
        options=selected_labels,
        index=0,
    )
    sort_column = label_to_col[sort_column_label]
    sort_ascending = st.checkbox("升序排序", value=False)

    page_size_detail = st.selectbox("每页显示行数", [10, 20, 50, 100], index=0, key="detail_page")
    total_rows = len(filtered)
    total_pages_detail = max(1, (total_rows + page_size_detail - 1) // page_size_detail)
    page_number_detail = st.number_input(
        "页码", min_value=1, max_value=total_pages_detail, value=1, step=1, key="detail_pn",
    )

    start_idx = (page_number_detail - 1) * page_size_detail
    end_idx = min(start_idx + page_size_detail, total_rows)

    sorted_df = filtered.sort_values(sort_column, ascending=sort_ascending).fillna("—")
    display_df = sorted_df.iloc[start_idx:end_idx][selected_columns].astype(str).replace("nan", "—")
    display_df = display_df.rename(columns=lambda c: COLUMN_LABELS.get(c, c))
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.dataframe(display_df, use_container_width=True)
    st.caption(f"显示第 {start_idx + 1} 到 {end_idx} 行，共 {total_rows} 行")

    st.subheader("数据统计摘要")
    if "price" in filtered.columns:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均值", f"{filtered['price'].mean():,.0f}")
        col2.metric("中位数", f"{filtered['price'].median():,.0f}")
        col3.metric("最小值", f"{filtered['price'].min():,.0f}")
        col4.metric("最大值", f"{filtered['price'].max():,.0f}")

    st.subheader("数据导出")
    col1, col2 = st.columns(2)
    with col1:
        csv_filtered = filtered.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载筛选后数据", data=csv_filtered,
                           file_name="杭州房价_筛选后数据.csv", mime="text/csv")
    with col2:
        csv_all = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载原始完整数据", data=csv_all,
                           file_name="杭州房价_原始数据.csv", mime="text/csv")

    footer()
