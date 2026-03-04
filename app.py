import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# ================= 页面配置（必须最前） =================
st.set_page_config(
    page_title="杭州房价分析仪表盘",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 全局样式（建议放在 set_page_config 后） =================
st.markdown("""
<style>

/* 页面整体留白 */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* 侧边栏背景变浅（立刻明显） */
section[data-testid="stSidebar"] > div {
    background-color: #f8fafc;
    padding: 1rem;
}

/* 多选框选中标签改成浅蓝风格（关键修改） */
span[data-baseweb="tag"] {
    background-color: #dbeafe !important;
    color: #1e3a8a !important;
    border-radius: 20px !important;
    border: none !important;
}

/* 标题更有层级 */
h1 { font-weight: 800; }
h2, h3 { font-weight: 700; }

/* 让 dataframe 外壳像卡片 */
div[data-testid="stDataFrame"] {
  background: white;
  border-radius: 14px;
  padding: 10px;
  box-shadow: 0 8px 30px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(148, 163, 184, 0.25);
}

/* 表格本体圆角 */
div[data-testid="stDataFrame"] > div {
  border-radius: 12px;
  overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# ================= 数据加载函数 =================
def load_data():
    """
    读取项目目录 data/ 下的 CSV（兼容本地 + Streamlit Cloud）
    - 优先读取清洗后数据：data/hangzhou_house_cleaned.csv
    - 不存在则读取原始数据：data/hangzhouhouseprice.csv
    """
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"

    cleaned_path = data_dir / "hangzhou_house_cleaned.csv"
    raw_path = data_dir / "hangzhouhouseprice.csv"

    # 优先读取清洗后数据，不存在则读取原始数据
    if cleaned_path.exists():
        try:
            df = pd.read_csv(cleaned_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(cleaned_path, encoding="gbk")
            except UnicodeDecodeError:
                df = pd.read_csv(cleaned_path, encoding="gb18030")

        source = f"读取清洗后数据：{cleaned_path}"
        cleaned_exists = True
    else:
        if not raw_path.exists():
            raise FileNotFoundError(
                f"未找到数据文件：{cleaned_path} 或 {raw_path}\n"
                f"请把 CSV 放到项目目录的 data/ 文件夹下。"
            )

        try:
            df = pd.read_csv(raw_path, encoding="gbk")
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(raw_path, encoding="gb18030")
            except UnicodeDecodeError:
                df = pd.read_csv(raw_path, encoding="utf-8-sig")

        df = df.drop_duplicates()
        if "House introduction" in df.columns:
            df["House introduction"] = df["House introduction"].fillna("未知")
        source = f"清洗数据不存在，读取原始数据：{raw_path}"
        cleaned_exists = False

    # 确保 House price 是数值型（否则 mean 会报错）
    if "House price" in df.columns:
        df["House price"] = pd.to_numeric(df["House price"], errors="coerce")

    return df, source, cleaned_exists

# ================= 先加载数据（一定要在 sidebar 指标前） =================
df, source, cleaned_exists = load_data()

# ================= 侧边栏（保持干净） =================
st.sidebar.markdown("## 数据概览")
st.sidebar.caption("全量数据概况（随筛选联动）")

st.sidebar.metric("总楼盘数", len(df))
st.sidebar.metric("平均价格", f"{df['House price'].mean():,.0f} 元/㎡")

st.sidebar.markdown("---")

st.sidebar.markdown("## 数据筛选")

# ================= 主页面 =================

plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

st.markdown("""
<h1 style='margin-bottom:0;'>杭州房地产市场分析仪表盘</h1>
<p style='color:gray; font-size:18px; margin-top:5px;'>
探索杭州各区域房价分布与趋势
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# 当前读的是哪份数据
if cleaned_exists:
    st.markdown(f"""
    <div style='background-color:#eef2ff;
    padding:15px;
    border-radius:10px;
    margin-bottom:20px;'>
    当前使用：清洗后的数据（hangzhou_house_cleaned.csv）
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("当前使用：原始数据（未找到清洗后的 hangzhou_house_cleaned.csv）")

# 表格默认显示在右侧
st.markdown("### 房源数据预览")
st.caption("展示当前筛选条件下的前 20 条记录")
st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
st.dataframe(df.head(20), use_container_width=True, height=520)
st.markdown("---")

# 区域选择（多选）
all_regions = sorted(df['House place'].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "选择区域",
    options=all_regions,
    default=all_regions[:5] if len(all_regions) > 5 else all_regions
)

# 价格范围选择
price_min, price_max = int(df['House price'].min()), int(df['House price'].max())
price_range = st.sidebar.slider(
    "价格范围 (元/㎡)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, min(price_max, 100000))
)

# 房产类型筛选
property_types = ['住宅', '商业', '别墅']
selected_types = st.sidebar.multiselect(
    "房产类型",
    options=property_types,
    default=property_types
)

# 应用筛选条件
filtered_df = df.copy()
if selected_regions:
    filtered_df = filtered_df[filtered_df['House place'].isin(selected_regions)]
if selected_types:
    filtered_df = filtered_df[filtered_df['property_type'].isin(selected_types)]
filtered_df = filtered_df[
    (filtered_df['House price'] >= price_range[0]) &
    (filtered_df['House price'] <= price_range[1])
]

# 显示筛选结果
st.sidebar.markdown("---")
st.sidebar.metric("筛选后楼盘数", len(filtered_df))
st.sidebar.metric("筛选后平均价", f"{filtered_df['House price'].mean():,.0f} 元/㎡")

# 主界面布局
st.markdown("## 分析面板")
st.markdown("---")

def beautify_plotly(fig, title=None, height=None, showlegend=True):
    """统一 Plotly 外观：白底、浅网格、合理边距、标题位置"""
    if title:
        fig.update_layout(title=dict(text=title, x=0.02, xanchor="left"))

    fig.update_layout(
        template="simple_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=60, b=20),
        font=dict(size=13),
        showlegend=showlegend,
    )

    if height:
        fig.update_layout(height=height)

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.25)")

    return fig

# ✅ A：Tab 名称去 emoji
tab1, tab2, tab3, tab4 = st.tabs(["区域分析", "价格分析", "价值发现", "数据详情"])

with tab1:
    import plotly.graph_objects as go

    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)

    def _gradient_colors(start_hex, end_hex, n):
        if n <= 1:
            return [start_hex]
        s = _hex_to_rgb(start_hex)
        e = _hex_to_rgb(end_hex)
        colors = []
        for i in range(n):
            t = i / (n - 1)
            rgb = (
                int(s[0] + (e[0] - s[0]) * t),
                int(s[1] + (e[1] - s[1]) * t),
                int(s[2] + (e[2] - s[2]) * t),
            )
            colors.append(_rgb_to_hex(rgb))
        return colors

    def _style_fig(fig, height=420):
        fig.update_layout(
            template="plotly_white",
            height=height,
            margin=dict(l=20, r=20, t=20, b=20),
            font=dict(size=12),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)", zeroline=False)
        fig.update_yaxes(showgrid=False, zeroline=False)
        return fig

    # ✅ A：标题去 emoji
    st.markdown("## 区域分析")
    st.caption("对比不同区域的价格水平、分布情况与热度（数量/均价）。")

    if filtered_df.empty:
        st.warning("当前筛选条件下没有数据，请调整左侧筛选。")
    else:
        region_stats = (
            filtered_df.groupby("House place")
            .agg({
                "House price": ["count", "mean", "median", "min", "max"],
                "avg_area": "mean"
            })
            .round(2)
        )
        region_stats.columns = ["楼盘数量", "平均价格", "价格中位数", "最低价格", "最高价格", "平均面积"]
        region_stats = region_stats.sort_values("价格中位数", ascending=False)

        st.markdown("### 价格对比与分布")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**中位数排名**")
            df1 = region_stats.head(15).copy()
            df1 = df1.sort_values("价格中位数", ascending=True).reset_index()
            colors1 = _gradient_colors("#eff6ff", "#1e3a8a", len(df1))

            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=df1["价格中位数"],
                y=df1["House place"],
                orientation="h",
                marker=dict(color=colors1, line=dict(color="rgba(30,58,138,0.25)", width=1)),
                text=df1["价格中位数"].round(0).astype(int),
                textposition="outside",
                cliponaxis=False,
                hovertemplate="区域：%{y}<br>中位数：%{x:.0f} 元/㎡<extra></extra>"
            ))
            fig1 = _style_fig(fig1, height=460)
            fig1.update_layout(xaxis_title="房价中位数（元/㎡）", yaxis_title="区域")
            fig1.update_yaxes(autorange="reversed")

            # ✅ C：隐藏右上角工具条
            st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown("**价格分布（箱线图）**")
            top_regions = region_stats.head(10).index.tolist()
            df2 = filtered_df[filtered_df["House place"].isin(top_regions)].copy()

            fig2 = go.Figure()
            ordered = list(reversed(top_regions))
            for r in ordered:
                d = df2[df2["House place"] == r]["House price"]
                fig2.add_trace(go.Box(
                    y=d,
                    name=r,
                    boxpoints="outliers",
                    marker=dict(color="rgba(37,99,235,0.35)"),
                    line=dict(color="rgba(37,99,235,0.75)", width=1.5),
                    fillcolor="rgba(37,99,235,0.18)",
                    hovertemplate=f"区域：{r}<br>价格：%{{y:.0f}} 元/㎡<extra></extra>"
                ))

            fig2 = _style_fig(fig2, height=460)
            fig2.update_layout(yaxis_title="价格（元/㎡）", xaxis_title="区域")
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### 区域热度分析")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**楼盘数量（Top 10）**")

            region_counts = filtered_df["House place"].value_counts().head(10).sort_values(ascending=True)
            df3 = region_counts.reset_index()
            df3.columns = ["区域", "楼盘数量"]
            colors3 = _gradient_colors("#f1f5f9", "#1e3a8a", len(df3))

            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=df3["楼盘数量"],
                y=df3["区域"],
                orientation="h",
                marker=dict(color=colors3, line=dict(color="rgba(30,58,138,0.22)", width=1)),
                text=df3["楼盘数量"],
                textposition="outside",
                cliponaxis=False,
                hovertemplate="区域：%{y}<br>楼盘数量：%{x}<extra></extra>"
            ))
            fig3 = _style_fig(fig3, height=420)
            fig3.update_layout(xaxis_title="楼盘数量", yaxis_title="区域")
            fig3.update_yaxes(autorange="reversed")

            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

        with col4:
            st.markdown("**平均房价（Top 10）**")

            region_avg_price = (
                filtered_df.groupby("House place")["House price"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
                .sort_values(ascending=True)
            )
            df4 = region_avg_price.reset_index()
            df4.columns = ["区域", "平均价格"]
            colors4 = _gradient_colors("#eff6ff", "#1e3a8a", len(df4))

            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=df4["平均价格"],
                y=df4["区域"],
                orientation="h",
                marker=dict(color=colors4, line=dict(color="rgba(30,58,138,0.22)", width=1)),
                text=df4["平均价格"].round(0).astype(int),
                textposition="outside",
                cliponaxis=False,
                hovertemplate="区域：%{y}<br>平均价格：%{x:.0f} 元/㎡<extra></extra>"
            ))
            fig4 = _style_fig(fig4, height=420)
            fig4.update_layout(xaxis_title="平均价格（元/㎡）", yaxis_title="区域")
            fig4.update_yaxes(autorange="reversed")

            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})

with tab2:
    # ✅ A：标题去 emoji
    st.markdown("## 价格分析")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("价格分布直方图")

        if not filtered_df.empty and "House price" in filtered_df.columns:
            fig5 = px.histogram(
                filtered_df,
                x="House price",
                nbins=50,
                marginal="box",
            )

            fig5.update_traces(
                marker=dict(color="rgba(91,143,249,0.85)"),
                selector=dict(type="histogram")
            )

            fig5.update_layout(
                template="simple_white",
                title_text="",
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="价格 (元/㎡)",
                yaxis_title="楼盘数量",
            )

            # ✅ C
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("当前筛选结果为空或缺少 House price 字段，无法绘制价格分布。")

    with col2:
        soft3 = ["#5B8FF9", "#5AD8A6", "#9270CA"]
        type_order = ["住宅", "别墅", "商业"]

        st.subheader("房产类型价格对比")

        if (
            not filtered_df.empty
            and "property_type" in filtered_df.columns
            and "House price" in filtered_df.columns
        ):
            exist_order = [t for t in type_order if t in filtered_df["property_type"].unique()]

            fig6 = px.box(
                filtered_df,
                x="property_type",
                y="House price",
                color="property_type",
                points="outliers",
                category_orders={"property_type": exist_order},
                color_discrete_sequence=soft3,
            )

            fig6.update_traces(
                line=dict(width=1),
                marker=dict(size=4, opacity=0.30),
            )

            fig6.update_layout(
                template="simple_white",
                title_text="",
                height=420,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="房产类型",
                yaxis_title="价格 (元/㎡)",
                legend_title_text="房产类型",
            )

            # ✅ C
            st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("缺少 property_type 或 House price 字段，无法绘制房产类型对比。")

        st.subheader("价格与面积的关系")

        if (
            not filtered_df.empty
            and "avg_area" in filtered_df.columns
            and "House price" in filtered_df.columns
        ):
            area_df = filtered_df.dropna(subset=["avg_area", "House price"])

            if not area_df.empty:
                if "property_type" in area_df.columns:
                    exist_order = [t for t in type_order if t in area_df["property_type"].unique()]

                    fig7 = px.scatter(
                        area_df,
                        x="avg_area",
                        y="House price",
                        color="property_type",
                        category_orders={"property_type": exist_order},
                        color_discrete_sequence=soft3,
                        hover_data=["House name", "House place"],
                    )
                    fig7.update_layout(legend_title_text="房产类型")
                else:
                    fig7 = px.scatter(
                        area_df,
                        x="avg_area",
                        y="House price",
                        hover_data=["House name", "House place"],
                    )
                    fig7.update_traces(marker=dict(color="rgba(91,143,249,0.45)"))

                fig7.update_traces(marker=dict(size=6, opacity=0.40))

                fig7.update_layout(
                    template="simple_white",
                    title_text="",
                    height=520,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title="平均面积 (㎡)",
                    yaxis_title="价格 (元/㎡)",
                )

                # ✅ C
                st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})

                if len(area_df) > 1:
                    correlation = area_df["avg_area"].corr(area_df["House price"])
                    st.metric("面积与价格相关性", f"{correlation:.3f}")
            else:
                st.info("当前筛选结果缺少有效面积数据，无法绘制『价格 vs 面积』。")
        else:
            st.info("缺少 avg_area 或 House price 字段，无法绘制『价格 vs 面积』。")

with tab3:
    # ✅ A：标题去 emoji
    st.markdown("## 价值发现")
    st.markdown("---")
    st.markdown("### 价值楼盘发现")
    st.caption("寻找价格显著低于区域基准价（中位数/均值）的潜在价值楼盘")

    if filtered_df.empty or "House place" not in filtered_df.columns or "House price" not in filtered_df.columns:
        st.warning("当前筛选条件下无数据，或缺少 House place / House price 字段。")
    else:
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

        base = filtered_df.copy()
        base["House price"] = pd.to_numeric(base["House price"], errors="coerce")
        base = base.dropna(subset=["House place", "House price"])
        base = base[base["House price"] > 0]

        region_counts = base["House place"].value_counts()
        keep_regions = region_counts[region_counts >= int(min_region_count)].index
        base = base[base["House place"].isin(keep_regions)]

        if base.empty:
            st.warning("应用『最少楼盘数』过滤后无数据。请降低阈值或放宽筛选条件。")
        else:
            if baseline == "区域中位数":
                region_base_price = base.groupby("House place")["House price"].median()
            else:
                region_base_price = base.groupby("House place")["House price"].mean()

            base["区域基准价"] = base["House place"].map(region_base_price)
            base["折扣比例"] = (1 - base["House price"] / base["区域基准价"]) * 100
            value_houses = base[base["折扣比例"] >= float(discount_threshold)].copy()

            if not value_houses.empty:
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("价值楼盘数量", f"{len(value_houses):,}")
                k2.metric("覆盖区域数", f"{value_houses['House place'].nunique():,}")
                k3.metric("平均折扣", f"{value_houses['折扣比例'].mean():.2f}%")
                k4.metric("最大折扣", f"{value_houses['折扣比例'].max():.2f}%")

                # ✅ A：提示去 emoji
                st.success(f"发现 {len(value_houses)} 个折扣 ≥ {discount_threshold}% 的价值楼盘（基准：{baseline}）")

                st.subheader("价值楼盘列表")

                display_columns = ["House name", "House place", "House price", "区域基准价", "折扣比例"]
                if "room_count" in value_houses.columns:
                    display_columns.append("room_count")
                if "avg_area" in value_houses.columns:
                    display_columns.append("avg_area")
                if "property_type" in value_houses.columns:
                    display_columns.append("property_type")

                sort_by = st.selectbox(
                    "排序方式",
                    options=["折扣比例", "House price", "区域基准价", "House place"],
                    index=0,
                    key="tab3_sort_by",
                )

                default_ascending = False if sort_by == "折扣比例" else True
                sort_ascending = st.checkbox(
                    "升序排序",
                    value=default_ascending,
                    key="tab3_sort_ascending",
                )

                value_houses_display = value_houses.sort_values(sort_by, ascending=sort_ascending)

                page_size = st.selectbox(
                    "每页显示数量",
                    [10, 20, 50, 100],
                    index=0,
                    key="tab3_page_size",
                )

                total_rows = len(value_houses_display)
                total_pages = max(1, (total_rows + page_size - 1) // page_size)

                page_number = st.number_input(
                    "页码",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    step=1,
                    key="tab3_page_number",
                )

                start_idx = (int(page_number) - 1) * int(page_size)
                end_idx = min(start_idx + int(page_size), total_rows)

                show_df = value_houses_display.iloc[start_idx:end_idx][display_columns].copy()
                show_df["House price"] = pd.to_numeric(show_df["House price"], errors="coerce").round(0)
                show_df["区域基准价"] = pd.to_numeric(show_df["区域基准价"], errors="coerce").round(0)
                show_df["折扣比例"] = pd.to_numeric(show_df["折扣比例"], errors="coerce").round(2)

                st.dataframe(show_df, use_container_width=True, height=420)
                st.caption(f"显示第 {start_idx+1} - {end_idx} 条，共 {total_rows} 条；第 {page_number}/{total_pages} 页")

                csv = value_houses_display[display_columns].to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="下载价值楼盘数据 (CSV)",
                    data=csv,
                    file_name=f"杭州价值楼盘_折扣≥{discount_threshold}%_{baseline}.csv",
                    mime="text/csv",
                    key="tab3_download_csv",
                )

                st.subheader("价值楼盘区域分布")
                colA, colB = st.columns(2)

                with colA:
                    region_value_counts = value_houses["House place"].value_counts().head(10)
                    fig8 = px.bar(
                        x=region_value_counts.values,
                        y=region_value_counts.index,
                        orientation="h",
                        labels={"x": "价值楼盘数量", "y": "区域"},
                        title="价值楼盘数量 Top10 区域",
                    )
                    fig8 = beautify_plotly(fig8, title=None, height=420, showlegend=False)
                    # ✅ C
                    st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False}, key="tab3_fig_region_top10")

                with colB:
                    fig9 = px.histogram(
                        value_houses,
                        x="折扣比例",
                        nbins=25,
                        title="折扣比例分布",
                    )
                    fig9 = beautify_plotly(fig9, title=None, height=420, showlegend=False)
                    # ✅ C
                    st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False}, key="tab3_fig_discount_hist")

            else:
                st.warning(f"在当前筛选条件下，未找到折扣 ≥ {discount_threshold}% 的价值楼盘（基准：{baseline}）。")
                st.info("建议：降低折扣阈值、放宽价格范围或减少『最少楼盘数』限制。")

with tab4:
    # ✅ A：标题去 emoji
    st.header("详细数据浏览")
    st.subheader("楼盘数据")

    all_columns = list(filtered_df.columns)
    default_columns = ['House name', 'House place', 'House price', 'property_type']
    if 'room_count' in all_columns:
        default_columns.append('room_count')
    if 'avg_area' in all_columns:
        default_columns.append('avg_area')

    selected_columns = st.multiselect(
        "选择显示的列",
        options=all_columns,
        default=default_columns
    )

    if selected_columns:
        sort_column = st.selectbox(
            "排序依据",
            options=selected_columns,
            index=0
        )
        sort_ascending = st.checkbox("升序排序", value=False)

        page_size_detail = st.selectbox("每页显示行数", [10, 20, 50, 100], index=0, key="detail_page")

        total_rows = len(filtered_df)
        total_pages_detail = max(1, total_rows // page_size_detail + 1)
        page_number_detail = st.number_input(
            "页码",
            min_value=1,
            max_value=total_pages_detail,
            value=1,
            step=1,
            key="detail_page_number"
        )

        start_idx_detail = (page_number_detail - 1) * page_size_detail
        end_idx_detail = min(start_idx_detail + page_size_detail, total_rows)

        sorted_df = filtered_df.sort_values(sort_column, ascending=sort_ascending)
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        st.dataframe(
            sorted_df.iloc[start_idx_detail:end_idx_detail][selected_columns],
            use_container_width=True
        )

        st.caption(f"显示第 {start_idx_detail + 1} 到 {end_idx_detail} 行，共 {total_rows} 行")

        st.subheader("数据统计摘要")
        if 'House price' in filtered_df.columns:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("平均值", f"{filtered_df['House price'].mean():,.0f}")
            col2.metric("中位数", f"{filtered_df['House price'].median():,.0f}")
            col3.metric("最小值", f"{filtered_df['House price'].min():,.0f}")
            col4.metric("最大值", f"{filtered_df['House price'].max():,.0f}")

    st.subheader("数据导出")

    col1, col2 = st.columns(2)

    with col1:
        csv_all = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载筛选后的完整数据",
            data=csv_all,
            file_name="杭州房价_筛选后数据.csv",
            mime="text/csv"
        )

    with col2:
        csv_original = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="下载原始完整数据",
            data=csv_original,
            file_name="杭州房价_原始数据.csv",
            mime="text/csv"
        )

# 页脚
st.markdown("---")
st.markdown("""
**数据说明**：
- 数据来源：模拟杭州房价数据
- 更新日期：2024年
- 分析工具：Python + Streamlit
""")