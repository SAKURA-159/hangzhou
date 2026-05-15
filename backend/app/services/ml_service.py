"""Machine learning service: house price prediction with Random Forest."""

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from app.models.house import House
from sqlalchemy.orm import Session

MODEL_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "price_model.pkl"

FEATURE_COLS = ["place", "room_count", "avg_area", "property_type"]
CAT_COLS = ["place", "property_type"]
NUM_COLS = ["room_count", "avg_area"]


def _prepare_data(db: Session) -> tuple[pd.DataFrame, pd.Series]:
    houses = db.query(House).filter(
        House.price > 0,
        House.avg_area > 0,
        House.room_count > 0,
        House.place.isnot(None),
    ).all()

    rows = [
        {
            "place": h.place,
            "room_count": float(h.room_count) if h.room_count else None,
            "avg_area": float(h.avg_area) if h.avg_area else None,
            "property_type": h.property_type or "住宅",
            "price": h.price,
        }
        for h in houses
    ]
    df = pd.DataFrame(rows).dropna()
    df["room_count"] = df["room_count"].clip(0, 10)
    df["avg_area"] = df["avg_area"].clip(0, 1000)
    df = df[df["price"] < df["price"].quantile(0.99)]  # drop extreme outliers

    X = df[FEATURE_COLS]
    y = np.log1p(df["price"])  # log-transform target for better distribution
    return X, y, df


def _build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
        ("num", StandardScaler(), NUM_COLS),
    ])
    return Pipeline([
        ("preprocess", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        )),
    ])


def train(db: Session) -> dict:
    X, y, df = _prepare_data(db)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42,
    )

    pipeline = _build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred_log = pipeline.predict(X_test)
    y_pred = np.expm1(y_pred_log)
    y_test_real = np.expm1(y_test)

    r2 = r2_score(y_test_real, y_pred)
    mae = mean_absolute_error(y_test_real, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test_real, y_pred))

    # Feature importance
    cat_names = pipeline.named_steps["preprocess"].named_transformers_["cat"].get_feature_names_out(CAT_COLS)
    all_names = list(cat_names) + NUM_COLS
    importances = pipeline.named_steps["model"].feature_importances_
    feat_imp = sorted(
        [{"feature": n, "importance": float(v)} for n, v in zip(all_names, importances)],
        key=lambda x: x["importance"],
        reverse=True,
    )

    # Save model
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(pipeline, f)

    # Actual vs predicted samples
    samples = [
        {"actual": float(y_test_real.iloc[i]), "predicted": float(y_pred[i])}
        for i in range(min(200, len(y_pred)))
    ]

    # Prediction error by price range
    df_result = pd.DataFrame({"actual": y_test_real, "predicted": y_pred})
    df_result["error_pct"] = abs(df_result["actual"] - df_result["predicted"]) / df_result["actual"] * 100
    price_bins = [0, 15000, 25000, 40000, 60000, float("inf")]
    price_labels = ["<1.5万", "1.5-2.5万", "2.5-4万", "4-6万", ">6万"]
    df_result["price_range"] = pd.cut(df_result["actual"], bins=price_bins, labels=price_labels)
    error_by_range = df_result.groupby("price_range", observed=False)["error_pct"].mean().round(1).to_dict()

    return {
        "r2": round(r2, 4),
        "mae": round(mae, 0),
        "rmse": round(rmse, 0),
        "samples": samples,
        "feature_importance": feat_imp,
        "error_by_range": error_by_range,
        "train_size": len(X_train),
        "test_size": len(X_test),
    }


def predict(features: dict) -> dict | None:
    if not MODEL_PATH.exists():
        return None

    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)

    row = pd.DataFrame([{
        "place": features.get("place", ""),
        "room_count": float(features.get("room_count", 3)),
        "avg_area": float(features.get("avg_area", 100)),
        "property_type": features.get("property_type", "住宅"),
    }])

    pred_log = pipeline.predict(row)[0]
    price = float(np.expm1(pred_log))

    # Confidence interval (std of individual trees)
    rf = pipeline.named_steps["model"]
    tree_preds = np.expm1([tree.predict(pipeline.named_steps["preprocess"].transform(row))[0] for tree in rf.estimators_])
    lower = float(np.percentile(tree_preds, 10))
    upper = float(np.percentile(tree_preds, 90))

    return {
        "predicted_price": round(price, 0),
        "confidence_interval": [round(lower, 0), round(upper, 0)],
        "features": features,
    }
