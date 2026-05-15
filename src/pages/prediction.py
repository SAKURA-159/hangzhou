"""智能预测 — standalone version (trains model client-side)."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.dashboard import chart_card, footer, section_header
from src.styles import beautify_plotly


MODEL_KEY = "ml_pipeline"


def _build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["place", "property_type"]),
        ("num", StandardScaler(), ["room_count", "avg_area"]),
    ])
    return Pipeline([
        ("preprocess", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=5,
            random_state=42, n_jobs=-1,
        )),
    ])


def render(df: pd.DataFrame) -> None:
    st.markdown("## 智能预测")
    st.caption("基于随机森林回归模型预测杭州房价，分析价格驱动因素。")

    tab_train, tab_predict = st.tabs(["模型训练与分析", "在线预测"])

    # Prepare data
    houses = df[df["price"] > 0].dropna(subset=["place", "price"])
    houses = houses[houses["avg_area"] > 0]
    houses = houses[houses["room_count"] > 0]
    houses = houses[houses["price"] < houses["price"].quantile(0.99)]

    with tab_train:
        st.markdown("### 随机森林回归模型")
        st.caption(f"使用区域、户型、面积、房产类型预测房价（{len(houses)} 条有效数据）。")

        if st.button("开始训练模型", type="primary"):
            with st.spinner("正在训练..."):
                features = houses[["place", "room_count", "avg_area", "property_type"]].copy()
                features["room_count"] = features["room_count"].clip(0, 10)
                features["avg_area"] = features["avg_area"].clip(0, 1000)
                target = np.log1p(houses["price"])

                X_train, X_test, y_train, y_test = train_test_split(
                    features, target, test_size=0.2, random_state=42,
                )

                pipeline = _build_pipeline()
                pipeline.fit(X_train, y_train)

                y_pred_log = pipeline.predict(X_test)
                y_pred = np.expm1(y_pred_log)
                y_test_real = np.expm1(y_test)

                result = {
                    "r2": r2_score(y_test_real, y_pred),
                    "mae": mean_absolute_error(y_test_real, y_pred),
                    "rmse": np.sqrt(mean_squared_error(y_test_real, y_pred)),
                    "actual": y_test_real.tolist(),
                    "predicted": y_pred.tolist(),
                }

                # Feature importance
                cat_names = pipeline.named_steps["preprocess"].named_transformers_["cat"].get_feature_names_out(["place", "property_type"])
                all_names = list(cat_names) + ["room_count", "avg_area"]
                importances = pipeline.named_steps["model"].feature_importances_
                result["feat_imp"] = sorted(
                    [{"feature": n, "importance": float(v)} for n, v in zip(all_names, importances)],
                    key=lambda x: x["importance"], reverse=True,
                )

                # Error by price range
                df_err = pd.DataFrame({"actual": y_test_real, "predicted": y_pred})
                df_err["error_pct"] = abs(df_err["actual"] - df_err["predicted"]) / df_err["actual"] * 100
                bins = [0, 15000, 25000, 40000, 60000, float("inf")]
                labels = ["<1.5万", "1.5-2.5万", "2.5-4万", "4-6万", ">6万"]
                df_err["range"] = pd.cut(df_err["actual"], bins=bins, labels=labels)
                result["error_by_range"] = df_err.groupby("range", observed=False)["error_pct"].mean().round(1).to_dict()

                st.session_state["ml_result"] = result
                st.session_state[MODEL_KEY] = pipeline

        result = st.session_state.get("ml_result")
        if not result:
            st.info("点击上方按钮开始训练模型。")
            return

        c1, c2, c3 = st.columns(3)
        c1.metric("R² 决定系数", f"{result['r2']:.3f}")
        c2.metric("MAE 平均误差", f"{result['mae']:,.0f} 元/㎡")
        c3.metric("RMSE 均方根误差", f"{result['rmse']:,.0f} 元/㎡")

        st.markdown("---")

        # Feature importance
        section_header("特征重要性", "各因素对房价预测的贡献程度。")
        feat_df = pd.DataFrame(result["feat_imp"]).head(10).sort_values("importance", ascending=True)

        fig1 = go.Figure(go.Bar(
            x=feat_df["importance"], y=feat_df["feature"], orientation="h",
            marker=dict(color="#489090", opacity=0.85, line=dict(width=0)),
            text=[f"{v:.3f}" for v in feat_df["importance"]],
            textposition="outside", textfont=dict(size=11, color="#7A8A8A"),
            cliponaxis=False, width=0.55,
        ))
        fig1 = beautify_plotly(fig1, height=320, showlegend=False, show_xgrid=True, show_ygrid=False)
        fig1.update_traces(marker=dict(cornerradius=6))
        fig1.update_layout(bargap=0.3)
        fig1.update_xaxes(showticklabels=False)
        fig1.update_yaxes(autorange="reversed", tickfont=dict(size=12, color="#2D3A3A"))
        chart_card(fig1)

        st.markdown("---")

        # Actual vs Predicted
        section_header("预测效果：实际 vs 预测", "")
        df_samples = pd.DataFrame({"actual": result["actual"], "predicted": result["predicted"]})

        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_samples["actual"], y=df_samples["predicted"],
            mode="markers", marker=dict(color="#489090", size=4, opacity=0.4, line=dict(width=0)),
            name="", hovertemplate="实际：%{x:,.0f}<br>预测：%{y:,.0f}<extra></extra>",
        ))
        max_val = max(df_samples["actual"].max(), df_samples["predicted"].max())
        fig2.add_trace(go.Scatter(
            x=[0, max_val], y=[0, max_val], mode="lines",
            line=dict(color="#2D5A5A", dash="dash", width=1), name="完美预测",
        ))
        fig2 = beautify_plotly(fig2, height=420, showlegend=True)
        fig2.update_layout(xaxis_title="实际价格 (元/㎡)", yaxis_title="预测价格 (元/㎡)")
        fig2.update_yaxes(tickformat=",.0f")
        fig2.update_xaxes(tickformat=",.0f")
        chart_card(fig2)

        # Error by range
        section_header("不同价位预测误差", "")
        error_data = result["error_by_range"]
        cols = st.columns(len(error_data))
        for i, (label, err) in enumerate(error_data.items()):
            cols[i].metric(label, f"{err:.1f}%")

    with tab_predict:
        st.markdown("### 在线房价预测")
        st.caption("输入房屋特征，模型给出预测价格区间。")

        if MODEL_KEY not in st.session_state:
            st.warning("请先在「模型训练与分析」页训练模型。")
            return

        col1, col2 = st.columns(2)
        with col1:
            place = st.selectbox("区域", options=sorted(houses["place"].dropna().unique()), index=0)
            room_count = st.slider("户型（室）", 1, 8, 3)
        with col2:
            avg_area = st.slider("面积 (㎡)", 30, 500, 100)
            property_type = st.selectbox("房产类型", ["住宅", "别墅", "商业"])

        if st.button("预测价格", type="primary"):
            pipeline = st.session_state[MODEL_KEY]
            row = pd.DataFrame([{
                "place": place, "room_count": float(room_count),
                "avg_area": float(avg_area), "property_type": property_type,
            }])
            pred_log = pipeline.predict(row)[0]
            price = float(np.expm1(pred_log))

            rf = pipeline.named_steps["model"]
            transformed = pipeline.named_steps["preprocess"].transform(row)
            tree_preds = np.expm1([tree.predict(transformed)[0] for tree in rf.estimators_])
            low, high = float(np.percentile(tree_preds, 10)), float(np.percentile(tree_preds, 90))

            st.markdown("---")
            c1, c2, c3 = st.columns([1, 1, 1.5])
            c1.metric("预测单价", f"{price:,.0f} 元/㎡")
            c2.metric("置信区间", f"{low:,.0f} ~ {high:,.0f}")
            if avg_area > 0:
                total = price * avg_area / 10000
                total_low = low * avg_area / 10000
                total_high = high * avg_area / 10000
                c3.metric("估算总价", f"{total:,.0f} 万",
                          delta=f"区间 {total_low:,.0f} ~ {total_high:,.0f} 万")

    footer()
