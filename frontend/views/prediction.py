"""智能预测 — train ML model and predict house prices."""

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

import api_client as api
from components.styles import beautify_plotly


def render() -> None:
    st.markdown("## 智能预测")
    st.caption("基于机器学习模型预测杭州房价，分析价格驱动因素。")

    tab_train, tab_predict = st.tabs(["模型训练与分析", "在线预测"])

    with tab_train:
        st.markdown("### 随机森林回归模型")
        st.caption("使用区域、户型、面积、房产类型作为特征，预测房价。")

        if st.button("开始训练模型", type="primary"):
            with st.spinner("正在训练模型，请稍候..."):
                resp = requests.post(f"{api.API_BASE}/api/ml/train", headers=api._headers(), timeout=120)
                if resp.status_code == 200:
                    result = resp.json()
                    st.session_state["ml_result"] = result
                else:
                    st.error(f"训练失败: {resp.json().get('detail', resp.text)}")

        result = st.session_state.get("ml_result")
        if not result:
            st.info("点击上方按钮开始训练模型。")
            return

        # Metrics
        st.markdown("### 模型性能")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("R² 决定系数", f"{result['r2']:.3f}")
        c2.metric("MAE 平均绝对误差", f"{result['mae']:,.0f} 元/㎡")
        c3.metric("RMSE 均方根误差", f"{result['rmse']:,.0f} 元/㎡")
        c4.metric("训练集 / 测试集", f"{result['train_size']} / {result['test_size']}")

        st.markdown("---")

        # Feature importance
        st.markdown("### 特征重要性")
        st.caption("各因素对房价预测的贡献程度。")

        imp_data = result["feature_importance"]
        feat_df = pd.DataFrame(imp_data).head(10)
        feat_df = feat_df.sort_values("importance", ascending=True)

        fig1 = go.Figure(
            go.Bar(
                x=feat_df["importance"],
                y=feat_df["feature"],
                orientation="h",
                marker=dict(color="#489090", opacity=0.85, line=dict(width=0)),
                text=[f"{v:.3f}" for v in feat_df["importance"]],
                textposition="outside",
                textfont=dict(size=11, color="#7A8A8A"),
                cliponaxis=False,
                width=0.55,
            )
        )
        fig1 = beautify_plotly(fig1, height=320, showlegend=False, show_xgrid=True, show_ygrid=False)
        fig1.update_traces(marker=dict(cornerradius=6))
        fig1.update_layout(bargap=0.3)
        fig1.update_xaxes(showticklabels=False)
        fig1.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#3A3E3B"))
        st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

        st.markdown("---")

        # Actual vs Predicted
        st.markdown("### 预测效果：实际 vs 预测")
        samples = result["samples"]
        df_samples = pd.DataFrame(samples)

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_samples["actual"], y=df_samples["predicted"],
            mode="markers",
            marker=dict(color="#489090", size=4, opacity=0.4, line=dict(width=0)),
            name="",
            hovertemplate="实际：%{x:,.0f}<br>预测：%{y:,.0f}<extra></extra>",
        ))
        max_val = max(df_samples["actual"].max(), df_samples["predicted"].max())
        fig2.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val],
            mode="lines",
            line=dict(color="#2D5A5A", dash="dash", width=1),
            name="完美预测",
        ))
        fig2 = beautify_plotly(fig2, height=420, showlegend=True)
        fig2.update_layout(xaxis_title="实际价格 (元/㎡)", yaxis_title="预测价格 (元/㎡)")
        fig2.update_yaxes(tickformat=",.0f")
        fig2.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        # Error by price range
        st.markdown("### 不同价位预测误差")
        error_data = result["error_by_range"]
        st.caption("平均绝对百分比误差 (MAPE) 按价格区间")

        cols = st.columns(len(error_data))
        for i, (label, err) in enumerate(error_data.items()):
            cols[i].metric(label, f"{err:.1f}%")

    with tab_predict:
        st.markdown("### 在线房价预测")
        st.caption("输入房屋特征，模型给出预测价格区间。")

        if "ml_result" not in st.session_state:
            st.warning("请先在「模型训练与分析」页训练模型。")
            return

        col1, col2 = st.columns(2)

        with col1:
            place = st.selectbox(
                "区域",
                options=["上城", "西湖", "拱墅", "滨江", "萧山", "余杭", "临平", "钱塘", "富阳", "临安", "下城"],
                index=4,
            )
            room_count = st.slider("户型（室）", 1, 8, 3)

        with col2:
            avg_area = st.slider("面积 (㎡)", 30, 500, 100)
            property_type = st.selectbox("房产类型", ["住宅", "别墅", "商业"])

        if st.button("预测价格", type="primary"):
            resp = requests.post(
                f"{api.API_BASE}/api/ml/predict",
                json={
                    "place": place,
                    "room_count": room_count,
                    "avg_area": float(avg_area),
                    "property_type": property_type,
                },
                headers=api._headers(),
                timeout=30,
            )
            if resp.status_code == 200:
                pred = resp.json()
                price = pred["predicted_price"]
                low, high = pred["confidence_interval"]

                st.markdown("---")
                c1, c2, c3 = st.columns([1, 1, 1.5])

                with c1:
                    st.metric("预测单价", f"{price:,.0f} 元/㎡")
                with c2:
                    st.metric("置信区间", f"{low:,.0f} ~ {high:,.0f}")

                if avg_area > 0:
                    total = price * avg_area / 10000
                    total_low = low * avg_area / 10000
                    total_high = high * avg_area / 10000
                    st.metric(
                        "估算总价",
                        f"{total:,.0f} 万",
                        delta=f"区间 {total_low:,.0f} ~ {total_high:,.0f} 万",
                    )
            else:
                st.error(f"预测失败: {resp.json().get('detail', resp.text)}")
