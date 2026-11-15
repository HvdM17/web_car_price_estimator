import json
from decimal import Decimal, ROUND_HALF_UP

import pytest
import joblib
from fastapi.testclient import TestClient

from backend.app import app, state
from backend.config import EXCHANGE_RATE_PATH, META_PATH, MODEL_PATH, OPTIONS_PATH
from backend.schemas import ExchangeRateConfig


@pytest.fixture(scope="module")
def client():
    state.update(
        pipeline=joblib.load(MODEL_PATH),
        meta=json.loads(META_PATH.read_text(encoding="utf-8")),
        options=json.loads(OPTIONS_PATH.read_text(encoding="utf-8")),
        exchange_rate=ExchangeRateConfig.model_validate(
            json.loads(EXCHANGE_RATE_PATH.read_text(encoding="utf-8"))
        ),
    )
    test_client = TestClient(app)
    yield test_client
    test_client.close()


def payload():
    return {"brand": "Maruti", "model": "Alto", "vehicle_age": 9, "km_driven": 120000, "seller_type": "Individual", "fuel_type": "Petrol", "transmission_type": "Manual", "mileage": 19.7, "engine": 796, "max_power": 46.3, "seats": 5}


def test_health_and_options(client):
    assert client.get("/health").json()["model_loaded"] is True
    assert client.get("/options").status_code == 200


def test_valid_prediction_structure(client):
    response = client.post("/predict", json=payload())
    assert response.status_code == 200
    body = response.json()
    assert body["predicted_price"] >= 0 and body["range_low"] <= body["range_high"]
    assert body["currency"] == "INR"
    assert body["model_name"] == "Random Forest"
    assert body["exchange_rate"] == 190.25
    assert body["exchange_rate_date"] == "2026-11-15"

    def to_idr(amount):
        return int(
            (Decimal(amount) * Decimal("190.25")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )

    assert body["predicted_price_idr"] == to_idr(body["predicted_price"])
    assert body["range_low_idr"] == to_idr(body["range_low"])
    assert body["range_high_idr"] == to_idr(body["range_high"])


def test_vehicle_age_limit(client):
    data = payload(); data["vehicle_age"] = 31
    assert client.post("/predict", json=data).status_code == 422


def test_negative_km(client):
    data = payload(); data["km_driven"] = -1
    assert client.post("/predict", json=data).status_code == 422


def test_mileage_limit(client):
    data = payload(); data["mileage"] = 2
    assert client.post("/predict", json=data).status_code == 422


def test_engine_limit(client):
    data = payload(); data["engine"] = 9000
    assert client.post("/predict", json=data).status_code == 422


def test_seats_zero(client):
    data = payload(); data["seats"] = 0
    assert client.post("/predict", json=data).status_code == 422


def test_missing_brand(client):
    data = payload(); del data["brand"]
    assert client.post("/predict", json=data).status_code == 422


def test_unknown_brand(client):
    data = payload(); data["brand"] = "Tesla"
    assert client.post("/predict", json=data).status_code == 422


def test_model_must_match_brand(client):
    data = payload(); data["model"] = "A4"
    assert client.post("/predict", json=data).status_code == 422


def test_bad_json(client):
    response = client.post("/predict", content="not-json", headers={"content-type": "application/json"})
    assert response.status_code == 422


def test_model_not_ready(client):
    old = state.copy()
    state.update(pipeline=None, meta=None, options=None, exchange_rate=None)
    try:
        assert client.post("/predict", json=payload()).status_code == 503
    finally:
        state.update(old)


def test_exchange_rate_not_ready(client):
    old = state.copy()
    state.update(exchange_rate=None)
    try:
        response = client.post("/predict", json=payload())
        assert response.status_code == 503
        assert response.json()["detail"] == "Kurs konversi belum siap"
    finally:
        state.update(old)
