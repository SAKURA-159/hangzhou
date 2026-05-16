"""Global CSS — teal + warm gold palette."""

import base64
from pathlib import Path

import streamlit as st
import plotly.graph_objects as go

# Palette from reference
BG = "#F0F0F0"           # light gray page
SIDEBAR = "#234545"      # dark teal
SURFACE = "#FFFFFF"      # white cards
TEXT = "#2D3A3A"         # dark teal-gray text
TEXT_SEC = "#7A8A8A"     # muted gray
BORDER = "#E0E5E5"        # light gray border
ACCENT = "#489090"       # teal accent
ACCENT_LIGHT = "#C8E0E0" # light teal
ACCENT_WARM = "#D89048"  # warm gold/orange


def inject_css() -> None:
    # Load background SVG
    bg_path = Path(__file__).resolve().parent / "bg.svg"
    bg_uri = ""
    if bg_path.exists():
        encoded = base64.b64encode(bg_path.read_bytes()).decode()
        bg_uri = f"url(data:image/svg+xml;base64,{encoded})"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

    .stApp {{
        background-color: {BG};
        background-image: {bg_uri};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
    }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1200px; }}

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] > div {{
        background: {SIDEBAR}; padding: 1.2rem 0.8rem;
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stCaption,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{ color: #B0C0C0 !important; }}
    section[data-testid="stSidebar"] h2 {{
        font-size: 0.82rem; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase;
    }}
    section[data-testid="stSidebar"] [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.04); border-radius: 8px; padding: 8px 12px;
        border: 1px solid rgba(255,255,255,0.05);
    }}
    section[data-testid="stSidebar"] [data-testid="stMetric"] label {{ color: #999 !important; font-size: 0.7rem; }}
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {{ color: #D8F0F0 !important; font-size: 1.15rem; }}
    section[data-testid="stSidebar"] button {{
        background: rgba(255,255,255,0.05) !important; color: #B0C0C0 !important;
        border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] button:hover {{ background: rgba(255,255,255,0.08) !important; }}

    /* --- Typography --- */
    h1 {{ font-weight: 700 !important; font-size: 1.5rem !important; color: {TEXT} !important; }}
    h2 {{ font-weight: 600 !important; font-size: 1.1rem !important; color: {TEXT} !important; }}
    h3 {{ font-weight: 600 !important; font-size: 0.95rem !important; color: {TEXT} !important; }}

    /* --- Metric cards --- */
    [data-testid="stMetric"] {{
        background: {SURFACE}; border-radius: 10px; padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid {BORDER};
    }}
    [data-testid="stMetric"] label {{
        color: {TEXT_SEC} !important; font-size: 0.72rem !important;
        text-transform: uppercase; letter-spacing: 0.05em;
    }}
    [data-testid="stMetricValue"] {{ font-weight: 700 !important; color: {TEXT} !important; }}

    /* --- Tables --- */
    [data-testid="stDataFrame"] {{
        background: {SURFACE}; border-radius: 10px; padding: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid {BORDER};
    }}
    [data-testid="stDataFrame"] > div {{ border-radius: 6px; overflow: hidden; }}
    [data-testid="stDataFrame"] th {{
        text-align: left !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        color: {TEXT} !important;
        padding: 8px 12px !important;
    }}
    [data-testid="stDataFrame"] td {{
        text-align: left !important;
        padding: 6px 12px !important;
        font-size: 0.82rem !important;
    }}
    [data-testid="stDataFrame"] div[data-testid="stTable"] td {{
        text-align: left !important;
    }}

    /* --- Input widgets consistency --- */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] {{
        border-radius: 6px !important; border-color: {BORDER} !important;
        font-size: 0.88rem !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus {{
        border-color: {ACCENT} !important; box-shadow: 0 0 0 2px rgba(72,144,144,0.15) !important;
    }}
    .stSlider > div {{ padding-top: 8px; }}

    /* --- Tags --- */
    span[data-baseweb="tag"] {{
        background-color: {ACCENT_LIGHT} !important; color: {ACCENT} !important;
        border-radius: 16px !important; font-weight: 500 !important; border: none !important;
    }}

    /* --- Forms --- */
    [data-testid="stForm"] {{
        background: {SURFACE}; border-radius: 12px; padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04); border: 1px solid {BORDER};
    }}

    /* --- Buttons --- */
    .stButton > button {{
        border-radius: 8px !important; font-weight: 500 !important;
        background: {ACCENT} !important; color: #FFF !important; border: none !important;
    }}
    .stButton > button:hover {{ background: #3A7878 !important; }}

    /* --- Sliders — override all red with teal --- */
    .stSlider [role="slider"] {{
        background: {ACCENT} !important;
        border-color: {ACCENT} !important;
        box-shadow: none !important;
    }}
    .stSlider [data-baseweb="slider"] div[style*="background"] {{
        background: {ACCENT} !important;
    }}
    .stSlider [data-baseweb="slider"] div[style*="background-color"] {{
        background-color: {ACCENT} !important;
    }}
    div[data-testid="stThumbValue"] {{
        background: {ACCENT} !important;
        color: #FFF !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stThumbValue"]::before {{
        border-bottom-color: {ACCENT} !important;
    }}
    div[data-testid="stTickBar"] div[style*="background"] {{
        background: {BORDER} !important;
    }}

    /* --- Number input --- */
    .stNumberInput [role="spinbutton"] {{
        border-color: {BORDER} !important;
    }}

    /* --- Select boxes --- */
    .stSelectbox [data-baseweb="select"] {{
        border-color: {BORDER} !important;
    }}

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab"] {{ border-radius: 6px 6px 0 0 !important; padding: 8px 20px !important; }}

    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-thumb {{ background: #CCC; border-radius: 3px; }}
    </style>
    """, unsafe_allow_html=True)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def gradient_colors(start_hex: str, end_hex: str, n: int) -> list[str]:
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


def beautify_plotly(
    fig: go.Figure,
    title: str | None = None,
    height: int | None = None,
    showlegend: bool = True,
    show_xgrid: bool = False,
    show_ygrid: bool = True,
) -> go.Figure:
    if title:
        fig.update_layout(title=dict(text=title, x=0.02, xanchor="left"))
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=10, t=40, b=0),
        font=dict(size=12, color=TEXT_SEC),
        showlegend=showlegend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="left", x=0, bgcolor="rgba(255,255,255,0.8)",
            bordercolor=BORDER, borderwidth=1,
        ),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(
        showgrid=show_xgrid, gridcolor="rgba(0,0,0,0.04)",
        zeroline=False, linecolor=BORDER,
    )
    fig.update_yaxes(
        showgrid=show_ygrid, gridcolor="rgba(0,0,0,0.04)",
        zeroline=False, linecolor=BORDER,
    )
    return fig
