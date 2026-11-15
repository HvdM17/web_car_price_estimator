
# Import library
import os
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Membaca dataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "cardekho_clean.csv")

df = pd.read_csv(DATA_PATH)


# Membersihkan data
valid_fuel = ['Petrol', 'Diesel', 'CNG']
valid_ownership = [
    'First Owner', 'Second Owner', 'Third Owner',
    'Fourth Owner', 'Fifth Owner'
]
valid_transmission = ['Manual', 'Automatic']

df_model = df[
    (df['price(in lakhs)'] <= 100) &
    (df['fuel_type'].isin(valid_fuel)) &
    (df['ownsership'].isin(valid_ownership)) &
    (df['transmission'].isin(valid_transmission))
].copy()


# Menentukan fitur dan target
fitur = [
    'insurance_validity',
    'fuel_type',
    'seats',
    'kms_driven',
    'ownsership',
    'transmission',
    'manufacturing_year'
]

X = df_model[fitur].copy()
y = df_model['price(in lakhs)'].copy()

categorical_features = [
    'insurance_validity', 'fuel_type',
    'ownsership', 'transmission'
]

numeric_features = [
    'seats', 'kms_driven', 'manufacturing_year'
]


# Membagi data training dan testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# Membuat preprocessing
preprocessor = ColumnTransformer(
    transformers=[
        ('kategori', OneHotEncoder(handle_unknown='ignore'), categorical_features),
        ('numerik', StandardScaler(), numeric_features)
    ]
)


# Membuat pipeline Random Forest
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('model', RandomForestRegressor(random_state=42))
])


# Menentukan parameter terbaik
param_grid = {
    'model__n_estimators': [100, 200],
    'model__max_depth': [None, 10, 20],
    'model__min_samples_split': [2, 5]
}

cv = KFold(n_splits=5, shuffle=True, random_state=42)

grid_search = GridSearchCV(
    pipeline,
    param_grid,
    cv=cv,
    scoring='neg_mean_absolute_error',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_train, y_train)


# Evaluasi model terbaik
best_model = grid_search.best_estimator_
y_pred = best_model.predict(X_test)

print("Parameter terbaik:", grid_search.best_params_)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))
print("R2:", r2_score(y_test, y_pred))


# Menyimpan model
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "car_price_model.joblib")
joblib.dump(best_model, MODEL_PATH)

print("Model berhasil disimpan:", MODEL_PATH)
