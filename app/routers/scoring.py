# app/routers/scoring.py
from fastapi import APIRouter, HTTPException, status
from app.schema.scoring import HealthQuizInput
from app.services.ml_service import predict_health_risk
from app.services.gemini_service import generate_action_plan

# Inisialisasi router secara presisi (Tanpa typo agar app.main bisa membacanya)
router = APIRouter(
    prefix="/scoring",
    tags=["Scoring & AI Action Plan"]
)

@router.post("/quiz", status_code=status.HTTP_200_OK)
async def process_health_quiz(payload: HealthQuizInput):
    """
    Endpoint Sakti TreeHealthy:
    1. Validasi input via Pydantic (Menjamin data bersih & anti-GIGO).
    2. Hitung skor risiko real-time via model CatBoost ter-tuning.
    3. Ambil referensi PDF Kemenkes (RAG) & generate personalized action plan 7 hari via Gemini 1.5 Flash.
    """
    try:
        # Langkah 1: Kalkulasi probabilitas risiko penyakit lewat mesin CatBoost
        ml_result = predict_health_risk(payload)
        
        # Ekstrak ringkasan data user dasar untuk dikirim ke Gemini Agent
        user_data_summary = {
            "age": payload.age,
            "gender": payload.gender,
            "bmi": payload.bmi
        }
        
        # Langkah 2: Suapi data ke Gemini AI Engine untuk generate rekomendasi terstruktur (JSON)
        ai_action_plan = generate_action_plan(user_data=user_data_summary, ml_result=ml_result)
        
        # Langkah 3: Kembalikan payload respons lengkap ke sisi Frontend
        return {
            "status": "success",
            "model_prediction": ml_result,
            "ai_engine_output": ai_action_plan
        }
        
    except FileNotFoundError as fnf:
        # Tangani error jika file model .pkl belum di-generate di folder weights
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(fnf)
        )
    except Exception as e:
        # Tangani error umum lainnya
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Gagal memproses kalkulasi kuis: {str(e)}"
        )