"""Chart builders — warm sage palette with subtle gradients."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.styles import beautify_plotly, gradient_colors

# Palette
ACCENT = "#489090"       # teal (主色)
ACCENT_DARK = "#2D5A5A"  # deep teal
ACCENT_LIGHT = "#C8E0E0" # light teal
WARM = "#D89048"         # warm gold accent
DARK = "#2D3A3A"
TEXT_SEC = "#7A8A8A"
LIGHT_BG = "rgba(72,144,144,0.08)"

# For scatter — distinct per-type colors
SCATTER_COLORS = {
    "住宅": "#489090",   # teal
    "别墅": "#D89048",   # warm gold (clearly different)
    "商业": "#8B9DA0",   # muted teal-gray
}


def _ht(lines: list[str]) -> str:
    return "<br>".join(lines) + "<extra></extra>"


def _multi_color_bar(x, y, n: int, opacity=0.85):
    """Build a horizontal bar with distinct multi-hue colors."""
    # Teal -> gold -> muted-blue cycle for visual variety
    stops = ["#489090", "#60A8A8", "#D89048", "#C07838", "#6B9EA0", "#489090"]
    colors = gradient_colors(stops[0], stops[-1], n) if n <= 4 else gradient_colors("#489090", "#D89048", n)
    return go.Bar(
        x=x, y=y, orientation="h",
        marker=dict(color=colors, opacity=opacity, line=dict(width=0)),
        textposition="outside",
        textfont=dict(size=11, color=TEXT_SEC),
        cliponaxis=False,
        width=0.35,
    )


# ==================== Tab 1: Region Analysis ====================

def region_median_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if "place" not in df.columns or "price" not in df.columns:
        return go.Figure()

    stats = (
        df.groupby("place")["price"]
        .median()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values(ascending=True)
    )

    bar = _multi_color_bar(stats.values, stats.index, len(stats))
    bar.text = [f" {v:,.0f} " for v in stats.values]
    bar.hovertemplate = _ht(["<b>%{y}</b>", "中位数：<b>%{x:,.0f}</b> 元/㎡"])

    fig = go.Figure(bar)
    fig = beautify_plotly(fig, height=440, showlegend=False, show_xgrid=True, show_ygrid=False)
    fig.update_traces(marker=dict(cornerradius=6))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color=DARK))
    return fig


def region_price_boxplot(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if "place" not in df.columns or "price" not in df.columns:
        return go.Figure()

    top_regions = (
        df.groupby("place")["price"]
        .median()
        .sort_values(ascending=False)
        .head(top_n)
        .index.tolist()
    )
    filtered = df[df["place"].isin(top_regions)]

    fig = go.Figure()
    for r in reversed(top_regions):
        d = filtered[filtered["place"] == r]["price"]
        fig.add_trace(go.Box(
            x=d, name=r, boxpoints="outliers",
            marker=dict(color=ACCENT_DARK, size=2, opacity=0.3),
            line=dict(color=ACCENT_DARK, width=1),
            fillcolor=LIGHT_BG,
            orientation="h",
            hovertemplate=_ht([f"<b>{r}</b>", "价格：<b>%{{x:,.0f}}</b> 元/㎡"]),
            width=0.5,
        ))

    fig = beautify_plotly(fig, height=440, showlegend=False, show_xgrid=True, show_ygrid=False)
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    fig.update_yaxes(tickfont=dict(size=12, color=DARK))
    return fig


def region_count_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if "place" not in df.columns:
        return go.Figure()

    counts = df["place"].value_counts().head(top_n).sort_values(ascending=True)

    bar = _multi_color_bar(counts.values, counts.index, len(counts), opacity=0.75)
    bar.text = counts.values
    bar.hovertemplate = _ht(["<b>%{y}</b>", "楼盘数量：<b>%{x}</b>"])

    fig = go.Figure(bar)
    fig = beautify_plotly(fig, height=400, showlegend=False, show_xgrid=True, show_ygrid=False)
    fig.update_traces(marker=dict(cornerradius=6))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color=DARK))
    return fig


def region_avg_price_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if "place" not in df.columns or "price" not in df.columns:
        return go.Figure()

    avg = (
        df.groupby("place")["price"]
        .mean()
        .sort_values(ascending=False)
        .head(top_n)
        .sort_values(ascending=True)
    )

    bar = _multi_color_bar(avg.values, avg.index, len(avg), opacity=0.75)
    bar.text = [f" {v:,.0f} " for v in avg.values]
    bar.hovertemplate = _ht(["<b>%{y}</b>", "均价：<b>%{x:,.0f}</b> 元/㎡"])

    fig = go.Figure(bar)
    fig = beautify_plotly(fig, height=400, showlegend=False, show_xgrid=True, show_ygrid=False)
    fig.update_traces(marker=dict(cornerradius=6))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color=DARK))
    return fig


# ==================== Tab 2: Price Analysis ====================

def price_histogram(df: pd.DataFrame, nbins: int = 50) -> go.Figure:
    if "price" not in df.columns:
        return go.Figure()

    median_val = df["price"].median()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["price"], nbinsx=nbins,
        marker=dict(color=ACCENT, opacity=0.7, line=dict(color="white", width=0.5)),
        hovertemplate=_ht(["价格：<b>%{x:,.0f}</b> 元/㎡", "数量：<b>%{y}</b>"]),
    ))

    fig.add_vline(
        x=median_val, line_dash="dash", line_color=ACCENT_DARK, line_width=1,
        annotation_text=f" 中位数 {median_val:,.0f} ",
        annotation_position="top right",
        annotation_font=dict(size=10, color=ACCENT_DARK),
    )

    fig = beautify_plotly(fig, height=420, showlegend=False)
    fig.update_layout(xaxis_title="价格 (元/㎡)", yaxis_title="楼盘数量", bargap=0.04)
    fig.update_xaxes(tickformat=",.0f")
    return fig


def property_type_boxplot(df: pd.DataFrame) -> go.Figure:
    if "property_type" not in df.columns or "price" not in df.columns:
        return go.Figure()

    exist_order = [t for t in ["住宅", "别墅", "商业"] if t in df["property_type"].unique()]

    fig = go.Figure()
    for t in exist_order:
        d = df[df["property_type"] == t]["price"]
        clr = SCATTER_COLORS.get(t, ACCENT)
        fig.add_trace(go.Box(
            y=d, name=t, boxpoints="outliers",
            marker=dict(color=clr, size=2, opacity=0.4),
            line=dict(color=clr, width=1.3),
            fillcolor=f"rgba({_rgba(clr, 0.1)})",
            hovertemplate=_ht([f"<b>{t}</b>", "价格：<b>%{{y:,.0f}}</b> 元/㎡"]),
            width=0.4,
        ))

    fig = beautify_plotly(fig, height=400, showlegend=True)
    fig.update_layout(xaxis_title=None, yaxis_title="价格 (元/㎡)")
    fig.update_yaxes(tickformat=",.0f")
    return fig


def price_vs_area_scatter(df: pd.DataFrame) -> go.Figure:
    if "avg_area" not in df.columns or "price" not in df.columns:
        return go.Figure()

    area_df = df.dropna(subset=["avg_area", "price"])
    if area_df.empty:
        return go.Figure()

    hover_cols = ["name", "place"] if "name" in area_df.columns else ["place"]

    if "property_type" in area_df.columns:
        exist_order = [t for t in ["住宅", "别墅", "商业"] if t in area_df["property_type"].unique()]
        color_map = {t: SCATTER_COLORS.get(t, ACCENT) for t in exist_order}
        fig = px.scatter(
            area_df, x="avg_area", y="price", color="property_type",
            category_orders={"property_type": exist_order},
            color_discrete_map=color_map,
            hover_data=hover_cols, opacity=0.55,
        )
        fig.update_layout(legend_title_text=None)
    else:
        fig = px.scatter(
            area_df, x="avg_area", y="price",
            hover_data=hover_cols, opacity=0.45,
        )
        fig.update_traces(marker=dict(color=ACCENT, size=5))

    fig.update_traces(marker=dict(size=5, line=dict(width=0)))
    fig = beautify_plotly(fig, height=480)
    fig.update_layout(xaxis_title="平均面积 (㎡)", yaxis_title="价格 (元/㎡)")
    fig.update_yaxes(tickformat=",.0f")
    return fig


def area_price_correlation(df: pd.DataFrame) -> float:
    area_df = df.dropna(subset=["avg_area", "price"])
    if len(area_df) < 2:
        return 0.0
    return area_df["avg_area"].corr(area_df["price"])


# ==================== Tab 3: Value Discovery ====================

def value_region_count_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if "place" not in df.columns:
        return go.Figure()

    counts = df["place"].value_counts().head(top_n)

    bar = _multi_color_bar(counts.values, counts.index, len(counts), opacity=0.75)
    bar.text = counts.values
    bar.hovertemplate = _ht(["<b>%{y}</b>", "价值楼盘：<b>%{x}</b> 个"])

    fig = go.Figure(bar)
    fig = beautify_plotly(fig, height=400, showlegend=False, show_xgrid=True, show_ygrid=False)
    fig.update_traces(marker=dict(cornerradius=6))
    fig.update_layout(bargap=0.3)
    fig.update_xaxes(showticklabels=False, title=None)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=12, color=DARK))
    return fig


def value_discount_histogram(df: pd.DataFrame, nbins: int = 25) -> go.Figure:
    if "折扣比例" not in df.columns:
        return go.Figure()

    median_disc = df["折扣比例"].median()

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df["折扣比例"], nbinsx=nbins,
        marker=dict(color=ACCENT, opacity=0.7, line=dict(color="white", width=0.5)),
        hovertemplate=_ht(["折扣：<b>%{x:.1f}%</b>", "数量：<b>%{y}</b>"]),
    ))

    fig.add_vline(
        x=median_disc, line_dash="dash", line_color=ACCENT_DARK, line_width=1,
        annotation_text=f" 中位数 {median_disc:.1f}% ",
        annotation_position="top right",
        annotation_font=dict(size=10, color=ACCENT_DARK),
    )

    fig = beautify_plotly(fig, height=400, showlegend=False)
    fig.update_layout(xaxis_title="折扣比例 (%)", yaxis_title="楼盘数量", bargap=0.04)
    return fig


# ==================== Helpers ====================

def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"{r},{g},{b},{alpha}"
