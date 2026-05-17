"""Login and registration page for standalone app — talks to FastAPI backend."""

import os
import streamlit as st
import requests

# Backend URL: Streamlit Cloud secrets → env var → localhost fallback
BACKEND_URL = st.secrets.get("BACKEND_URL") or os.getenv("BACKEND_URL", "http://localhost:8000")


def _api_register(username: str, email: str, password: str) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/api/auth/register",
        json={"username": username, "email": email, "password": password},
        timeout=10,
    )
    if resp.status_code == 409:
        raise ValueError("用户名或邮箱已存在")
    if resp.status_code >= 400:
        detail = resp.json().get("detail", "注册失败")
        raise ValueError(detail)
    return resp.json()


def _api_login(username: str, password: str) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    if resp.status_code == 401:
        raise ValueError("用户名或密码错误")
    if resp.status_code >= 400:
        detail = resp.json().get("detail", "登录失败")
        raise ValueError(detail)
    return resp.json()


def render_auth() -> None:
    # Hero section
    st.markdown("""
    <div style='text-align:center; padding:50px 20px 20px 20px;'>
        <div style='display:inline-block;margin:0 auto 14px auto;'>
            <svg width='60' height='60' viewBox='0 0 64 64' fill='none' xmlns='http://www.w3.org/2000/svg'>
                <rect x='6' y='30' width='22' height='30' rx='2' fill='#489090'/>
                <rect x='36' y='30' width='22' height='30' rx='2' fill='#489090'/>
                <path d='M32 6L6 30h52L32 6z' fill='#489090'/>
                <rect x='14' y='44' width='7' height='16' rx='1.5' fill='#C8E0E0'/>
                <rect x='43' y='44' width='7' height='16' rx='1.5' fill='#C8E0E0'/>
            </svg>
        </div>
        <h2 style='font-weight:700;color:#2D3A3A;margin-bottom:4px;'>杭州房地产市场分析</h2>
        <p style='font-size:0.9rem;color:#7A8A8A;margin-bottom:0;'>
            探索房价分布 · 发现价值洼地 · 洞察市场趋势
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 1, 1.2])
    with col2:
        tab_login, tab_register = st.tabs(["登录", "注册"])

        with tab_login:
            with st.form("login_form"):
                st.markdown(
                    "<p style='font-weight:600;font-size:0.95rem;color:#2D3A3A;margin-bottom:12px;'>"
                    "欢迎回来</p>",
                    unsafe_allow_html=True,
                )
                username = st.text_input("用户名", placeholder="请输入用户名", key="login_username")
                password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
                submitted = st.form_submit_button("登 录", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("请填写用户名和密码")
                    else:
                        try:
                            result = _api_login(username, password)
                            st.session_state["access_token"] = result["access_token"]
                            st.session_state["user"] = result["user"]
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))
                        except requests.ConnectionError:
                            st.error("无法连接后端服务，请先启动后端或使用离线模式")

        with tab_register:
            with st.form("register_form"):
                st.markdown(
                    "<p style='font-weight:600;font-size:0.95rem;color:#2D3A3A;margin-bottom:12px;'>"
                    "创建新账号</p>",
                    unsafe_allow_html=True,
                )
                new_username = st.text_input("用户名", placeholder="请输入用户名", key="reg_username")
                new_email = st.text_input("邮箱", placeholder="请输入邮箱", key="reg_email")
                new_password = st.text_input("密码", type="password", placeholder="至少4位", key="reg_password")
                submitted = st.form_submit_button("注 册", use_container_width=True)

                if submitted:
                    if not new_username or not new_email or not new_password:
                        st.error("请填写所有字段")
                    elif len(new_password) < 4:
                        st.error("密码至少4位")
                    else:
                        try:
                            _api_register(new_username, new_email, new_password)
                            st.success("注册成功！请切换到登录页登录。")
                        except ValueError as e:
                            st.error(str(e))
                        except requests.ConnectionError:
                            st.error("无法连接后端服务，请先启动后端或使用离线模式")

        # Offline fallback
        st.markdown(
            "<p style='text-align:center;margin-top:16px;color:#7A8A8A;font-size:0.78rem;'>"
            "—— 或 ——</p>",
            unsafe_allow_html=True,
        )
        if st.button("离线访客模式", use_container_width=True, key="guest_btn"):
            st.session_state["access_token"] = "guest"
            st.session_state["user"] = {"username": "访客", "is_admin": False}
            st.rerun()
