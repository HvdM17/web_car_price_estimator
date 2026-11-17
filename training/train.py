"""Train the documented CarDekho price-estimation pipeline."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "cardekho_dataset.csv"
OUT_DATA = ROOT / "data" / "cardekho_clean.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "model_kelompok_X.joblib"
HOLDOUT_METRICS_PATH = MODEL_DIR / "holdout_metrics.json"
MODEL_COMPARISON_PATH = MODEL_DIR / "model_comparison.csv"
FEATURES = ["brand", "model", "vehicle_age", "km_driven", "seller_type", "fuel_type", "transmission_type", "mileage", "engine", "max_power", "seats"]
NUMERIC = ["vehicle_age", "km_driven", "mileage", "engine", "max_power", "seats"]
CATEGORICAL = ["brand", "model", "seller_type", "fuel_type", "transmission_type"]


def clean_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH).drop(columns=["Unnamed: 0"], errors="ignore").drop_duplicates()
    df["brand"] = df["brand"].replace({"ISUZU": "Isuzu"})
    for column in NUMERIC + ["selling_price"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=FEATURES + ["selling_price"])
    return df[(df["seats"] >= 2) & (df["km_driven"] <= 1_000_000)]


def main() -> None:
    df = clean_data()
    print(f"clean rows: {len(df)}", flush=True)
    OUT_DATA.parent.mkdir(exist_ok=True)
    df.to_csv(OUT_DATA, index=False)
    MODEL_DIR.mkdir(exist_ok=True)
    X, y = df[FEATURES], df["selling_price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    preprocessor = ColumnTransformer([
        ("num", Pipeline([( "scale", StandardScaler())]), NUMERIC),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
    ])
    models = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=30, random_state=42, n_jobs=1),
        "gradient_boosting": GradientBoostingRegressor(random_state=42),
    }
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    scores = {}
    candidates = {}
    for name, estimator in models.items():
        for target_transform in ["raw", "log1p"]:
            key = f"{name}_{target_transform}"
            print(f"cv: {key}", flush=True)
            pipeline = Pipeline([( "preprocess", preprocessor), ("model", estimator)])
            candidate = pipeline if target_transform == "raw" else TransformedTargetRegressor(
                regressor=pipeline, func=np.log1p, inverse_func=np.expm1
            )
            score = -cross_val_score(candidate, X_train, y_train, cv=cv, scoring="neg_mean_absolute_error", n_jobs=1)
            scores[key] = {"cv_mae_mean": float(score.mean()), "cv_mae_std": float(score.std())}
            candidates[key] = candidate
    best_key = min(scores, key=lambda key: scores[key]["cv_mae_mean"])
    best_name, target_transform = best_key.rsplit("_", 1)
    print(f"best: {best_key}", flush=True)
    base = candidates[best_key]
    grid = {
        "random_forest": {"model__n_estimators": [30, 100], "model__max_depth": [None, 20]},
        "gradient_boosting": {"model__n_estimators": [100, 200], "model__learning_rate": [0.05, 0.1]},
        "linear_regression": {},
    }[best_name]
    if target_transform == "log1p":
        grid = {f"regressor__{key}": value for key, value in grid.items()}
    search = GridSearchCV(base, grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=1)
    search.fit(X_train, y_train)
    print("grid complete", flush=True)
    model = search.best_estimator_
    prediction = model.predict(X_test)
    holdout_metrics = {
        "mae": float(mean_absolute_error(y_test, prediction)),
        "rmse": float(np.sqrt(mean_squared_error(y_test, prediction))),
        "r2": float(r2_score(y_test, prediction)),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "random_state": 42,
    }
    final_model = clone(model).fit(X, y)
    joblib.dump(final_model, MODEL_PATH, compress=3)
    HOLDOUT_METRICS_PATH.write_text(json.dumps(holdout_metrics, indent=2), encoding="utf-8")
    comparison = [
        {"candidate": key, **value}
        for key, value in scores.items()
    ]
    pd.DataFrame(comparison).sort_values("cv_mae_mean").to_csv(MODEL_COMPARISON_PATH, index=False)
    models_by_brand = {brand: sorted(group["model"].unique().tolist()) for brand, group in df.groupby("brand")}
    (MODEL_DIR / "options.json").write_text(json.dumps({"brands": sorted(models_by_brand), "models_by_brand": models_by_brand, "seller_types": sorted(df["seller_type"].unique()), "fuel_types": sorted(df["fuel_type"].unique()), "transmission_types": sorted(df["transmission_type"].unique())}, indent=2), encoding="utf-8")
    (MODEL_DIR / "feature_columns.json").write_text(json.dumps(FEATURES, indent=2), encoding="utf-8")
    model_names = {"linear_regression": "Linear Regression", "random_forest": "Random Forest", "gradient_boosting": "Gradient Boosting"}
    metadata = {
        "model": best_name,
        "model_name": model_names[best_name],
        "target_transform": target_transform,
        "best_params": search.best_params_,
        "metrics": holdout_metrics,
        "mae": holdout_metrics["mae"],
        "evaluation_train_rows": len(X_train),
        "evaluation_test_rows": len(X_test),
        "final_fit_rows": len(X),
        "holdout_metrics_file": HOLDOUT_METRICS_PATH.name,
        "model_comparison_file": MODEL_COMPARISON_PATH.name,
        "cv_scores": scores,
    }
    (MODEL_DIR / "model_meta.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({"model": best_name, "metrics": holdout_metrics, "artifacts": [str(MODEL_PATH), str(OUT_DATA), str(MODEL_DIR / "model_meta.json"), str(HOLDOUT_METRICS_PATH), str(MODEL_COMPARISON_PATH), str(MODEL_DIR / "feature_columns.json"), str(MODEL_DIR / "options.json")]}, indent=2))


if __name__ == "__main__":
    main()
