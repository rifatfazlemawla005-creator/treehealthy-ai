# check_models.py
import google.generativeai as genai
from app.config import settings

# Konfigurasi API Key lo
genai.configure(api_key=settings.GOOGLE_API_KEY)

print("🔍 Sedang memeriksa daftar model yang tersedia di API Key lo...\n")

try:
    # Mengambil list model resmi dari Google Studio
    available_models = genai.list_models()
    
    print("📋 MODEL YANG MENDUKUNG EMBEDDING:")
    print("-" * 60)
    
    found_any = False
    for model in available_models:
        # Cek apakah model tersebut punya method 'embedContent'
        if 'embedContent' in model.supported_generation_methods:
            print(f"🔹 Name       : {model.name}")
            print(f"🔸 Description: {model.description}")
            print(f"🔺 Output Dim : {model.output_token_limit if hasattr(model, 'output_token_limit') else '768'}")
            print("-" * 60)
            found_any = True
            
    if not found_any:
        print("⚠️ Waduh, gak ada model embedding yang terdeteksi aktif di API Key lo!")
        
except Exception as e:
    print(f"❌ Gagal mengambil data model dari Google: {str(e)}")
    print("Pastiin GOOGLE_API_KEY di file .env lo udah bener dan valid ya, bro!")