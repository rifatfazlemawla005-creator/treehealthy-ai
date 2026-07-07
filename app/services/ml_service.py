# app/services/ml_service.py
import os
import pickle
import pandas as pd
from app.schema.scoring import HealthQuizInput

# Path lokasi model pkl CatBoost teroptimal
MODEL_PATH = os.path.join(os.path.dirname(__file__), "weights", "mock_ptm_model.pkl")

def convert_real_age_to_cdc_scale(age: int) -> int:
    """
    Mengonversi umur asli (tahun) menjadi skala kategori 1-13 sesuai standar CDC BRFSS.
    """
    if 18 <= age <= 24: return 1
    elif 25 <= age <= 29: return 2
    elif 30 <= age <= 34: return 3
    elif 35 <= age <= 39: return 4
    elif 40 <= age <= 44: return 5
    elif 45 <= age <= 49: return 6
    elif 50 <= age <= 54: return 7
    elif 55 <= age <= 59: return 8
    elif 60 <= age <= 64: return 9
    elif 65 <= age <= 69: return 10
    elif 70 <= age <= 74: return 11
    elif 75 <= age <= 79: return 12
    elif age >= 80: return 13
    else: return 1 # Fallback untuk usia di bawah 18 tahun

def predict_health_risk(user_input: HealthQuizInput) -> dict:
    """
    Menghitung probabilitas risiko PTM menggunakan model CatBoost teroptimal.
    Menerima input bersih dari Pydantic (Anti-GIGO).
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"❌ File model tidak ditemukan di {MODEL_PATH}. Harap jalankan training dulu, bro!")
        
    # 1. Pre-processing & Standarisasi data input kuis
    cdc_age = convert_real_age_to_cdc_scale(user_input.age)
    cdc_sex = 1 if user_input.gender.upper() == "MALE" else 0
    cdc_bp = 1 if user_input.high_bp else 0
    cdc_chol = 1 if user_input.high_chol else 0
    cdc_smoker = 1 if user_input.smoker else 0
    user_bmi = float(user_input.bmi)
    
    # 2. Wajib dibuat jadi DataFrame dengan nama kolom yang PERSIS sama saat training!
    # Urutan: ['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker']
    input_data = pd.DataFrame([{
        'Age': int(cdc_age),
        'Sex': int(cdc_sex),
        'BMI': user_bmi,
        'HighBP': int(cdc_bp),
        'HighChol': int(cdc_chol),
        'Smoker': int(cdc_smoker)
    }])
    
    # 3. Load Model CatBoost ter-tuning via Pickle
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
        
    # 4. Prediksi Probabilitas Kelas 1 (Berisiko Diabetes)
    probability = model.predict_proba(input_data)[0][1]
    probability_percentage = round(probability * 100, 2)
    
    # 5. Mapping Risk Tier (Kuantifikasi Skala Risiko Medis)
    if probability_percentage < 35:
        risk_tier = "LOW RISK"
    elif 35 <= probability_percentage < 65:
        risk_tier = "MEDIUM RISK"
    else:
        risk_tier = "HIGH RISK"
        
    return {
        "category": "METABOLIC",
        "probability": probability_percentage,
        "risk_tier": risk_tier
    }