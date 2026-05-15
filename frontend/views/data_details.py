"""数据详情 page — browse raw data, statistics summary, data export."""

import pandas as pd
import streamlit as st

import api_client as api
from components.dashboard import footer, kpi_row, section_header
from components.filters import apply_client_filters, render_sidebar


def render() -> None:
    st.header("详细数据浏览")
    st.subheader("楼盘数据")

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

    section_header("数据浏览", "查看和导出当前筛选条件下的房源数据。")

    all_columns = list(df.columns)
    default_columns = ["name", "place", "price", "property_type"]
    if "room_count" in all_columns:
        default_columns.append("room_count")
    if "avg_area" in all_columns:
        default_columns.append("avg_area")

    selected_columns = st.multiselect(
        "选择显示的列",
        options=all_columns,
        default=default_columns,
    )

    if not selected_columns:
        return

    sort_column = st.selectbox("排序依据", options=selected_columns, index=0)
    sort_ascending = st.checkbox("升序排序", value=False)

    page_size_detail = st.selectbox("每页显示行数", [10, 20, 50, 100], index=0, key="detail_page")

    total_rows = len(df)
    total_pages_detail = max(1, (total_rows + page_size_detail - 1) // page_size_detail)
    page_number_detail = st.number_input(
        "页码", min_value=1, max_value=total_pages_detail, value=1, step=1, key="detail_page_number",
    )

    start_idx = (page_number_detail - 1) * page_size_detail
    end_idx = min(start_idx + page_size_detail, total_rows)

    sorted_df = df.sort_values(sort_column, ascending=sort_ascending).fillna("—")
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.dataframe(
        sorted_df.iloc[start_idx:end_idx][selected_columns],
        use_container_width=True,
    )

    st.caption(f"显示第 {start_idx + 1} 到 {end_idx} 行，共 {total_rows} 行")

    st.subheader("数据统计摘要")
    if "price" in df.columns:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("平均值", f"{df['price'].mean():,.0f}")
        col2.metric("中位数", f"{df['price'].median():,.0f}")
        col3.metric("最小值", f"{df['price'].min():,.0f}")
        col4.metric("最大值", f"{df['price'].max():,.0f}")

    st.subheader("数据导出")

    col1, col2 = st.columns(2)

    with col1:
        csv_filtered = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下载筛选后的完整数据",
            data=csv_filtered,
            file_name="杭州房价_筛选后数据.csv",
            mime="text/csv",
        )

    with col2:
        all_data = api.get_houses({"page": 1, "page_size": 10000})
        all_df = pd.DataFrame(all_data.get("items", []))
        csv_all = all_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="下载原始完整数据",
            data=csv_all,
            file_name="杭州房价_原始数据.csv",
            mime="text/csv",
        )

    footer()
