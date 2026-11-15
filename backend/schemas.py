from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

try:
    from .config import BRANDS, FUEL_TYPES, SELLER_TYPES, TRANSMISSION_TYPES
except ImportError:
    from config import BRANDS, FUEL_TYPES, SELLER_TYPES, TRANSMISSION_TYPES


def _check_in(value: str, allowed: list[str], label: str) -> str:
    if value not in allowed:
        raise ValueError(f"{label} tidak dikenal: {value}")
    return value


class CarInput(BaseModel):
    brand: str = Field(min_length=1, max_length=40)
    model: str = Field(min_length=1, max_length=50)
    vehicle_age: int = Field(ge=0, le=30)
    km_driven: int = Field(ge=0, le=1_000_000)
    seller_type: str
    fuel_type: str
    transmission_type: str
    mileage: float = Field(ge=4, le=40)
    engine: int = Field(ge=500, le=7000)
    max_power: float = Field(ge=30, le=700)
    seats: int = Field(ge=2, le=9)

    @field_validator("brand")
    @classmethod
    def check_brand(cls, v: str) -> str:
        return _check_in(v, BRANDS, "merek")

    @field_validator("seller_type")
    @classmethod
    def check_seller(cls, v: str) -> str:
        return _check_in(v, SELLER_TYPES, "tipe penjual")

    @field_validator("fuel_type")
    @classmethod
    def check_fuel(cls, v: str) -> str:
        return _check_in(v, FUEL_TYPES, "bahan bakar")

    @field_validator("transmission_type")
    @classmethod
    def check_transmission(cls, v: str) -> str:
        return _check_in(v, TRANSMISSION_TYPES, "transmisi")


class PredictionOutput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    predicted_price: int
    currency: str = "INR"
    range_low: int
    range_high: int
    predicted_price_idr: int
    range_low_idr: int
    range_high_idr: int
    exchange_rate: float
    exchange_rate_date: date
    range_note: str
    model_name: str = "Random Forest"
    model_version: str


class ExchangeRateConfig(BaseModel):
    base_currency: Literal["INR"]
    display_currency: Literal["IDR"]
    inr_to_idr: Decimal = Field(gt=0, allow_inf_nan=False)
    updated_at: date
    source: str = Field(min_length=1)


class HealthOutput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    model_version: str | None = None


class OptionsOutput(BaseModel):
    brands: list[str]
    models_by_brand: dict[str, list[str]]
    seller_types: list[str]
    fuel_types: list[str]
    transmission_types: list[str]
