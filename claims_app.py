# --- FASTAPI BACKEND ---
# File: claims_app.py

from fastapi import FastAPI
from pydantic import BaseModel, Field
from enum import Enum
import joblib
import pandas as pd
from prophet.serialize import model_from_json
import json
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
with open('prophet_model.json', 'r') as fin:
    prophet_model = model_from_json(json.load(fin))

residual_model = joblib.load("best_residual_model_LinearRegression.pkl")
scaler = joblib.load("residual_model_scaler.pkl")
metadata = joblib.load("model_metadata.pkl")

# Enums for categorical constraints
class ClaimTypeEnum(str, Enum):
    routine = "Routine"
    emergency = "Emergency"
    inpatient = "Inpatient"
    outpatient = "Outpatient"

class ClaimSubmissionMethodEnum(str, Enum):
    paper = "Paper"
    online = "Online"
    phone = "Phone"

class ProviderSpecialtyEnum(str, Enum):
    cardiology = "Cardiology"
    pediatrics = "Pediatrics"
    neurology = "Neurology"
    general = "General Practice"
    orthopedics = "Orthopedics"

class PatientEmploymentStatusEnum(str, Enum):
    retired = "Retired"
    student = "Student"
    employed = "Employed"
    unemployed = "Unemployed"

class PatientMaritalStatusEnum(str, Enum):
    married = "Married"
    single = "Single"
    divorced = "Divorced"
    widowed = "Widowed"

class PatientGenderEnum(str, Enum):
    male = "M"
    female = "F"

class ClaimStatusEnum(str, Enum):
    pending = "Pending"
    approved = "Approved"
    denied = "Denied"

class ClaimData(BaseModel):
    PatientAge: float
    PatientIncome: float
    PatientGender: PatientGenderEnum
    PatientMaritalStatus: PatientMaritalStatusEnum
    ClaimType: ClaimTypeEnum
    PatientEmploymentStatus: PatientEmploymentStatusEnum
    ClaimDate: str  # Format: 'YYYY-MM-DD'
    DiagnosisCode: str = Field(..., pattern=r"^[A-Za-z]{2}\d{3}$")
    ProcedureCode: str = Field(..., pattern=r"^[A-Za-z]{2}\d{3}$")
    ProviderSpecialty: ProviderSpecialtyEnum
    ClaimStatus: ClaimStatusEnum
    ProviderLocation: str
    ClaimSubmissionMethod: ClaimSubmissionMethodEnum

@app.post("/predict/")
async def predict(data: ClaimData):
    try:
        df = pd.DataFrame([data.dict()])

        # Time series forecast
        prophet_df = df[['ClaimDate']].rename(columns={'ClaimDate': 'ds'})
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])
        forecast = prophet_model.predict(prophet_df)
        prophet_pred = forecast['yhat'].values[0]

        # Feature engineering
        df['ClaimDate'] = pd.to_datetime(df['ClaimDate'])
        df['Year'] = df['ClaimDate'].dt.year
        df['Month'] = df['ClaimDate'].dt.month
        df['DayOfWeek'] = df['ClaimDate'].dt.dayofweek
        df['is_weekend'] = (df['DayOfWeek'] >= 5).astype(int)
        df['quarter'] = df['ClaimDate'].dt.quarter
        df['weekofyear'] = df['ClaimDate'].dt.isocalendar().week.astype(int)

        df['Age_ClaimType'] = df['PatientAge'] * df['ClaimType'].astype('category').cat.codes
        df['Income_Employment'] = df['PatientIncome'] * df['PatientEmploymentStatus'].astype('category').cat.codes

        # One-hot encoding
        X = df[metadata['features']]
        X = pd.get_dummies(X, drop_first=True)
        X = X.reindex(columns=metadata['train_columns'], fill_value=0)
        X_scaled = scaler.transform(X)

        residual_pred = residual_model.predict(X_scaled)[0]

        return {
            "status": "success",
            "predictions": {
                "prophet": float(prophet_pred),
                "residual": float(residual_pred),
                "final": float(prophet_pred + residual_pred)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
