"""Train the documented CarDekho price-estimation pipeline."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
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
    for name, estimator in models.items():
        print(f"cv: {name}", flush=True)
        pipeline = Pipeline([( "preprocess", preprocessor), ("model", estimator)])
        score = -cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="neg_mean_absolute_error", n_jobs=1)
        scores[name] = {"cv_mae_mean": float(score.mean()), "cv_mae_std": float(score.std())}
    best_name = min(scores, key=lambda name: scores[name]["cv_mae_mean"])
    print(f"best: {best_name}", flush=True)
    base = Pipeline([( "preprocess", preprocessor), ("model", models[best_name])])
    grid = {
        "random_forest": {"model__n_estimators": [30], "model__max_depth": [None]},
        "gradient_boosting": {"model__n_estimators": [100, 200], "model__learning_rate": [0.05, 0.1]},
        "linear_regression": {},
    }[best_name]
    search = GridSearchCV(base, grid, cv=cv, scoring="neg_mean_absolute_error", n_jobs=1)
    search.fit(X_train, y_train)
    print("grid complete", flush=True)
    model = search.best_estimator_
    prediction = model.predict(X_test)
    metrics = {"mae": float(mean_absolute_error(y_test, prediction)), "rmse": float(np.sqrt(mean_squared_error(y_test, prediction))), "r2": float(r2_score(y_test, prediction))}
    joblib.dump(model, MODEL_PATH, compress=3)
    models_by_brand = {brand: sorted(group["model"].unique().tolist()) for brand, group in df.groupby("brand")}
    (MODEL_DIR / "options.json").write_text(json.dumps({"brands": sorted(models_by_brand), "models_by_brand": models_by_brand, "seller_types": sorted(df["seller_type"].unique()), "fuel_types": sorted(df["fuel_type"].unique()), "transmission_types": sorted(df["transmission_type"].unique())}, indent=2), encoding="utf-8")
    (MODEL_DIR / "feature_columns.json").write_text(json.dumps(FEATURES, indent=2), encoding="utf-8")
    (MODEL_DIR / "model_meta.json").write_text(json.dumps({"model": best_name, "best_params": search.best_params_, "metrics": metrics, "mae": metrics["mae"], "train_rows": len(X_train), "test_rows": len(X_test), "cv_scores": scores}, indent=2), encoding="utf-8")
    print(json.dumps({"model": best_name, "metrics": metrics, "artifacts": [str(MODEL_PATH), str(OUT_DATA), str(MODEL_DIR / "model_meta.json"), str(MODEL_DIR / "feature_columns.json"), str(MODEL_DIR / "options.json")]}, indent=2))


if __name__ == "__main__":
    main()
