# app/services/gemini_service.py
import json
from google import genai
from google.genai import types
from app.config import settings

# Inisialisasi Client Baru
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

def get_rag_context_from_db(bmi: float, risk_tier: str) -> str:
    """
    Fungsi simulasi pencarian vector DB.
    Silakan hubungkan ke real pgvector lo nanti, bro.
    """
    return """
    Rekomendasi Kemenkes RI untuk Risiko Metabolik/Diabetes: 
    Penderita dengan risiko sedang wajib membatasi konsumsi gula maksimal 4 sendok makan per hari, 
    melakukan aktivitas fisik aerobik ringan (seperti jalan cepat) minimal 30 menit sehari atau 150 menyit per minggu, 
    serta menjaga hidrasi dengan minum air putih minimal 2 liter sehari.
    """

def generate_action_plan(user_data: dict, ml_result: dict) -> dict:
    """
    Menggunakan model gacor gemini-2.5-flash untuk generate 
    checklist kesehatan 7 hari secara dinamis (JSON Murni).
    """
    rag_context = get_rag_context_from_db(user_data["bmi"], ml_result["risk_tier"])
    
    prompt = f"""
    Anda adalah Dokter Spesialis Edukasi PTM (Penyakit Tidak Menular) dari Kemenkes RI.
    Tugas Anda adalah membuat rencana aksi (action plan) 7 hari kustom untuk pasien berdasarkan data berikut:
    
    DATA PASIEN:
    - Umur: {user_data['age']} tahun
    - Gender: {user_data['gender']}
    - BMI: {user_data['bmi']}
    - Hasil Prediksi ML CatBoost: Risiko {ml_result['risk_tier']} (Probabilitas: {ml_result['probability']}%)
    
    REFERENSI RESMI KEMENKES (RAG CONTEXT):
    \"\"\"{rag_context}\"\"\"
    
    Wajib mengembalikan output dalam format JSON MURNI sesuai dengan skema target.
    Penting: Variasikan tugas dari hari 1 sampai 7 (jangan dicopas ulang) berdasarkan referensi Kemenkes di atas!
    """
    
    try:
        # PAKAI MODEL 3.5 FLASH YANG SUDAH TERBUKTI GACOR & ANTI-503
        response = client.models.generate_content(
            model='gemini-3.5-flash', # <--- GANTI JADI INI
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        result_json = json.loads(response.text)
        return result_json
        
    except Exception as e:
        print(f"⚠️ Error pada SDK Baru Gemini: {str(e)}")
        # Pintu darurat aman jika terjadi limitasi jaringan
        return {
            "ai_explanation": f"Gagal memproses rekomendasi pintar secara real-time. Risiko Anda saat ini adalah {ml_result['risk_tier']}.",
            "weekly_checklist": [
                {"day": i, "tasks": ["Batasi konsumsi gula sesuai anjuran Kemenkes", "Lakukan aktivitas fisik ringan 30 menit"]}
                for i in range(1, 8)
            ]
        }