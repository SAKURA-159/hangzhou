"""杭州房地产市场分析仪表盘 — Standalone Streamlit Cloud Edition.

Deploy: push to GitHub → connect to streamlit.io/cloud
"""

import importlib

import streamlit as st

from src.data import load_data
from src.styles import inject_css

st.set_page_config(
    page_title="杭州房价分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# --------------- Load Data ---------------
df = load_data()
if df.empty:
    st.error("无法加载数据文件，请确保 data/ 目录下有 CSV 文件。")
    st.stop()

# --------------- Sidebar Branding ---------------
st.sidebar.markdown("""
<div style='padding:0.5rem 0 1rem 0;'>
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:4px;'>
        <svg width='32' height='32' viewBox='0 0 64 64' fill='none' xmlns='http://www.w3.org/2000/svg'>
            <rect x='6' y='30' width='22' height='30' rx='2' fill='#60B0B0'/>
            <rect x='36' y='30' width='22' height='30' rx='2' fill='#60B0B0'/>
            <path d='M32 6L6 30h52L32 6z' fill='#60B0B0'/>
            <rect x='14' y='44' width='7' height='16' rx='1.5' fill='#234545'/>
            <rect x='43' y='44' width='7' height='16' rx='1.5' fill='#234545'/>
        </svg>
        <span style='color:#DDD;font-weight:700;font-size:0.95rem;'>杭州房市</span>
    </div>
    <p style='color:#777;font-size:0.72rem;margin:0;'>Hangzhou Real Estate</p>
</div>
""", unsafe_allow_html=True)

# --------------- Navigation ---------------
page_names = ["区域分析", "价格分析", "价值发现", "智能预测", "数据详情"]
page_modules = {
    "区域分析": "src.pages.region_analysis",
    "价格分析": "src.pages.price_analysis",
    "价值发现": "src.pages.value_discovery",
    "智能预测": "src.pages.prediction",
    "数据详情": "src.pages.data_details",
}

st.sidebar.markdown("## 导航")
selected_page = st.sidebar.radio("选择页面", page_names, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.caption(f"全库共 {len(df):,} 条房源")

# --------------- Page Header ---------------
st.markdown(f"""
<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;'>
    <div>
        <h1 style='margin-bottom:2px;'>杭州房地产市场分析</h1>
        <p style='color:#7A8A8A; font-size:0.9rem; margin:0;'>
            探索各区域房价分布 · 挖掘价值楼盘 · 洞察市场趋势
        </p>
    </div>
    <div style='background:#E0F0F0;padding:10px 16px;
                border-radius:8px;text-align:right;'>
        <p style='color:#7A8A8A;font-size:0.7rem;margin:0;font-weight:500;'>当前页面</p>
        <p style='color:#2D3A3A;font-size:0.95rem;margin:0;font-weight:700;'>{selected_page}</p>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("---")

# --------------- Dispatch to Page ---------------
module_name = page_modules[selected_page]
mod = importlib.import_module(module_name)
mod.render(df)
