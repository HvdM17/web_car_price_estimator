import json
import logging
from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_HALF_UP

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

try:
    # Works with: uvicorn backend.app:app (run from project root)
    from .config import EXCHANGE_RATE_PATH, FEATURE_ORDER, FRONTEND_DIR, META_PATH, MODEL_PATH, OPTIONS_PATH
    from .schemas import CarInput, ExchangeRateConfig, HealthOutput, OptionsOutput, PredictionOutput
except ImportError:
    # Also works with: cd backend; uvicorn app:app --reload
    from config import EXCHANGE_RATE_PATH, FEATURE_ORDER, FRONTEND_DIR, META_PATH, MODEL_PATH, OPTIONS_PATH
    from schemas import CarInput, ExchangeRateConfig, HealthOutput, OptionsOutput, PredictionOutput

logger = logging.getLogger("uvicorn.error")

state = {"pipeline": None, "meta": None, "options": None, "exchange_rate": None}


def _convert_to_idr(amount: int, rate: Decimal) -> int:
    return int((Decimal(amount) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        state["pipeline"] = joblib.load(MODEL_PATH)
        state["meta"] = json.loads(META_PATH.read_text(encoding="utf-8"))
        state["options"] = json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
        logger.info("Model dimuat: %s", MODEL_PATH.name)
    except FileNotFoundError:
        state["pipeline"] = None
        state["meta"] = None
        state["options"] = None
        logger.warning("Model belum tersedia: %s", MODEL_PATH.name)
    except Exception:
        # Server tetap jalan. /health akan melaporkan model_loaded: false.
        state["pipeline"] = None
        state["meta"] = None
        state["options"] = None
        logger.exception("Gagal memuat model")

    try:
        rate_data = json.loads(EXCHANGE_RATE_PATH.read_text(encoding="utf-8"))
        state["exchange_rate"] = ExchangeRateConfig.model_validate(rate_data)
    except FileNotFoundError:
        state["exchange_rate"] = None
        logger.error("Konfigurasi kurs belum tersedia: %s", EXCHANGE_RATE_PATH)
    except Exception:
        state["exchange_rate"] = None
        logger.exception("Konfigurasi kurs tidak valid: %s", EXCHANGE_RATE_PATH)
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


@app.get("/options", response_model=OptionsOutput)
def options():
    if state["options"] is None:
        raise HTTPException(status_code=503, detail="Opsi belum siap")
    return state["options"]


@app.post("/predict", response_model=PredictionOutput)
def predict(payload: CarInput):
    pipeline = state["pipeline"]
    meta = state["meta"]
    if pipeline is None or meta is None:
        raise HTTPException(status_code=503, detail="Model belum siap")
    exchange_rate = state["exchange_rate"]
    if exchange_rate is None:
        raise HTTPException(status_code=503, detail="Kurs konversi belum siap")

    models_by_brand = (state["options"] or {}).get("models_by_brand", {})
    if payload.model not in models_by_brand.get(payload.brand, []):
        raise HTTPException(status_code=422, detail="Model tidak sesuai dengan merek")

    row = pd.DataFrame([payload.model_dump()])[FEATURE_ORDER]

    try:
        price = float(pipeline.predict(row)[0])
    except Exception:
        logger.exception("Prediksi gagal")
        raise HTTPException(status_code=500, detail="Terjadi kesalahan internal")

    price = max(price, 0.0)
    mae = float(meta["mae"])
    predicted_price = round(price)
    range_low = round(max(price - mae, 0.0))
    range_high = round(price + mae)

    return PredictionOutput(
        predicted_price=predicted_price,
        range_low=range_low,
        range_high=range_high,
        predicted_price_idr=_convert_to_idr(predicted_price, exchange_rate.inr_to_idr),
        range_low_idr=_convert_to_idr(range_low, exchange_rate.inr_to_idr),
        range_high_idr=_convert_to_idr(range_high, exchange_rate.inr_to_idr),
        exchange_rate=float(exchange_rate.inr_to_idr),
        exchange_rate_date=exchange_rate.updated_at,
        range_note=(
            "Rentang ± MAE dari data uji, bukan interval kepercayaan statistik"
        ),
        model_name=str(meta.get("model_name", "Random Forest")),
        model_version=MODEL_PATH.name,
    )


# Frontend dilayani paling akhir agar tidak menutupi endpoint API.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
