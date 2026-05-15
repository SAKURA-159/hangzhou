"""Login and registration page with modern design."""

import streamlit as st

import api_client as api


def render_auth() -> None:
    # Hero section
    st.markdown("""
    <div style='text-align:center; padding:60px 20px 20px 20px;'>
        <div style='display:inline-block;margin:0 auto 16px auto;'>
            <svg width='64' height='64' viewBox='0 0 64 64' fill='none' xmlns='http://www.w3.org/2000/svg'>
                <rect x='2' y='28' width='26' height='34' rx='2' fill='#489090'/>
                <rect x='36' y='28' width='26' height='34' rx='2' fill='#489090'/>
                <path d='M32 4L2 28h60L32 4z' fill='#489090'/>
                <rect x='12' y='44' width='8' height='18' rx='2' fill='#C8E0E0'/>
                <rect x='44' y='44' width='8' height='18' rx='2' fill='#C8E0E0'/>
            </svg>
        </div>
        <h1 style='font-size:2rem;font-weight:700;color:#2D3A3A;margin-bottom:6px;'>
            杭州房地产市场分析
        </h1>
        <p style='font-size:0.95rem;color:#7A8A8A;margin-bottom:0;'>
            探索房价分布 · 发现价值洼地 · 洞察市场趋势
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.2, 1, 1.2])

    with col2:
        tab_login, tab_register = st.tabs(["登录", "注册"])

        with tab_login:
            with st.form("login_form"):
                st.markdown("<p style='font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:12px;'>欢迎回来</p>", unsafe_allow_html=True)
                username = st.text_input("用户名", placeholder="请输入用户名", key="login_username")
                password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
                submitted = st.form_submit_button("登 录", use_container_width=True)

                if submitted:
                    if not username or not password:
                        st.error("请填写用户名和密码")
                    else:
                        try:
                            result = api.login(username, password)
                            st.session_state["access_token"] = result["access_token"]
                            st.session_state["user"] = result["user"]
                            st.rerun()
                        except ValueError as e:
                            st.error(str(e))

        with tab_register:
            with st.form("register_form"):
                st.markdown("<p style='font-weight:600;font-size:0.95rem;color:#334155;margin-bottom:12px;'>创建新账号</p>", unsafe_allow_html=True)
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
                            api.register(new_username, new_email, new_password)
                            st.success("注册成功！请切换到登录页登录。")
                        except ValueError as e:
                            st.error(str(e))
