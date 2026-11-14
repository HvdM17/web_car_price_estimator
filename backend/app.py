import json
import logging
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from config import FEATURE_ORDER, FRONTEND_DIR, META_PATH, MODEL_PATH
from schemas import CarInput, HealthOutput, PredictionOutput

logger = logging.getLogger("uvicorn.error")

state = {"pipeline": None, "meta": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["pipeline"] = joblib.load(MODEL_PATH)
        state["meta"] = json.loads(META_PATH.read_text(encoding="utf-8"))
        logger.info("Model dimuat: %s", MODEL_PATH.name)
    except FileNotFoundError:
        state["pipeline"] = None
        state["meta"] = None
        logger.warning("Model belum tersedia: %s", MODEL_PATH.name)
    except Exception:
        # Server tetap jalan. /health akan melaporkan model_loaded: false.
        state["pipeline"] = None
        state["meta"] = None
        logger.exception("Gagal memuat model")
    yield


app = FastAPI(title="Estimator Harga Mobil Bekas", lifespan=lifespan)


@app.get("/health", response_model=HealthOutput)
def health():
    loaded = state["pipeline"] is not None and state["meta"] is not None
    return HealthOutput(
        status="ok",
        model_loaded=loaded,
        model_version=MODEL_PATH.name if loaded else None,
    )


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: CarInput):
    pipeline = state["pipeline"]
    meta = state["meta"]
    if pipeline is None or meta is None:
        raise HTTPException(status_code=503, detail="Model belum siap")

    row = pd.DataFrame([payload.model_dump()])[FEATURE_ORDER]

    try:
        price = float(pipeline.predict(row)[0])
    except Exception:
        logger.exception("Prediksi gagal")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal")

    price = max(price, 0.0)
    mae = float(meta["mae"])

    return PredictionOutput(
        predicted_price=round(price),
        range_low=round(max(price - mae, 0.0)),
        range_high=round(price + mae),
        range_note=(
            "Rentang ± MAE dari data uji, bukan interval kepercayaan statistik"
        ),
        model_version=MODEL_PATH.name,
    )


# Frontend dilayani paling akhir agar tidak menutupi endpoint API.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
