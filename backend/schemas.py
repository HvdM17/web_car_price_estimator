from pydantic import BaseModel, ConfigDict, Field, field_validator

from config import BRANDS, FUEL_TYPES, SELLER_TYPES, TRANSMISSION_TYPES


def _check_in(value: str, allowed: list[str], label: str) -> str:
    if value not in allowed:
        raise ValueError(f"{label} tidak dikenal: {value}")
    return value


class CarInput(BaseModel):
    brand: str
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
    range_note: str
    model_version: str


class HealthOutput(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    status: str
    model_loaded: bool
    model_version: str | None = None
