# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scoring 

app = FastAPI(
    title="TreeHealthy AI Engine",
    description="Backend API untuk Prediksi Risiko PTM (CatBoost) & Personalized Action Plan 7 Hari (Gemini RAG Kemenkes)",
    version="1.0.0"
)

# 🛠️ SETTING CORS: Biar frontend gak kena block pas nembak API local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Di fase dev di-allow semua dulu, nanti pas prod bisa dikunci ke domain tertentu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🚀 Registrasi Router scoring kuis kita
app.include_router(scoring.router)

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "Welcome to TreeHealthy AI Engine API! Buka /docs untuk mencoba kuis."
    }