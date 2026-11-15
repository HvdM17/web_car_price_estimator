from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent        # backend/
PROJECT_DIR = BASE_DIR.parent                     # root proyek
FRONTEND_DIR = PROJECT_DIR / "frontend"
MODEL_DIR = PROJECT_DIR / "models"
MODEL_PATH = MODEL_DIR / "model_kelompok_X.joblib"
META_PATH = MODEL_DIR / "model_meta.json"
OPTIONS_PATH = MODEL_DIR / "options.json"
FEATURE_COLUMNS_PATH = MODEL_DIR / "feature_columns.json"
DATASET_PATH = PROJECT_DIR / "data" / "cardekho_dataset.csv"
FEATURE_COLUMNS = [
    "brand", "model", "vehicle_age", "km_driven", "seller_type",
    "fuel_type", "transmission_type", "mileage", "engine", "max_power", "seats",
]

NUMERIC_FEATURES = ["vehicle_age", "km_driven", "mileage", "engine", "max_power", "seats"]
CATEGORICAL_FEATURES = ["brand", "model", "seller_type", "fuel_type", "transmission_type"]
FEATURE_ORDER = FEATURE_COLUMNS

# Daftar ini diambil dari data setelah cleaning. D4 (Mercedes-AMG) belum diputuskan.
BRANDS = [
    "Audi", "BMW", "Bentley", "Datsun", "Ferrari", "Force", "Ford", "Honda",
    "Hyundai", "Isuzu", "Jaguar", "Jeep", "Kia", "Land Rover", "Lexus", "MG",
    "Mahindra", "Maruti", "Maserati", "Mercedes-AMG", "Mercedes-Benz", "Mini",
    "Nissan", "Porsche", "Renault", "Rolls-Royce", "Skoda", "Tata", "Toyota",
    "Volkswagen", "Volvo",
]
FUEL_TYPES = ["Petrol", "Diesel", "CNG", "LPG", "Electric"]
SELLER_TYPES = ["Dealer", "Individual", "Trustmark Dealer"]
TRANSMISSION_TYPES = ["Manual", "Automatic"]
