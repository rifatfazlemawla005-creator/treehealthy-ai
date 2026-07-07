# test_gemini.py
import json
from google import genai
from app.config import settings

print("==================================================")
print("🚀 AUTOMATED MULTI-MODEL GEMINI TESTING")
print("==================================================")

# List model gacor yang tersedia di akun lo, diurutkan dari yang terbaik
MODELS_TO_TEST = [
    'gemini-2.5-flash',
    'gemini-3.5-flash',
    'gemini-2.0-flash'
]

# Prompt standar untuk test format output
prompt = """
Buatlah rencana aksi kesehatan acak untuk 2 hari dalam format JSON murni.
Struktur wajib seperti ini:
{
    "status": "sukses",
    "pesan": "Koneksi berhasil",
    "sample_checklist": [
        {"day": 1, "task": "Minum air putih 2 liter"},
        {"day": 2, "task": "Jalan kaki 30 menit"}
    ]
}
"""

client = genai.Client(api_key=settings.GOOGLE_API_KEY)
model_sukses = None

for model_name in MODELS_TO_TEST:
    print(f"\n🛰️ Mencoba menembak API via model: {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )
        
        # Validasi JSON Parsing
        data = json.loads(response.text)
        print(f"✅ BERHASIL! Model {model_name} merespons dengan JSON valid.")
        print(f"💬 Pesan dari AI: {data['pesan']}")
        
        # Simpan nama model yang sukses untuk kita pakai di FastAPI nanti
        model_sukses = model_name
        break # Keluar dari loop karena udah nemu yang sukses
        
    except Exception as e:
        print(f"❌ Model {model_name} GAGAL/MOGOK.")
        print(f"ℹ️ Detail Error: {str(e)[:150]}...")
        print("-" * 30)

print("\n==================================================")
if model_sukses:
    print(f"🏆 KESIMPULAN: Pakai model '{model_sukses}' untuk FastAPI lo, bro!")
else:
    print("❌ KESIMPULAN: Semua model gagal. Cek limit kuota atau billing API Key lo!")
print("==================================================")