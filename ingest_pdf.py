# ingest_pdf.py
import os
import google.generativeai as genai
from pypdf import PdfReader
from app.database.connection import get_db_connection
from app.config import settings

# Konfigurasi Google API Key secara native
genai.configure(api_key=settings.GOOGLE_API_KEY)

# PERBAIKAN 1: Sesuaikan nama key agar pas dengan nama file asli di folder lo
PDF_MAPPING = {
    "Bahaya Hipertensi, Upaya Pencegahan d...pdf": "CARDIOVASCULAR",
    "Lawan Diabetes dengan Cerdik.pdf": "METABOLIC",
    "Kelola Stress.pdf": "RESPIRATORY",
    "kualitas tidur.pdf": "RESPIRATORY"
}

def split_text_into_chunks(text: str, chunk_size=1000, chunk_overlap=200) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - chunk_overlap
    return chunks

def ingest_all_pdfs():
    pdf_dir = "app/static/docs"
    
    actual_files = os.listdir(pdf_dir)
    hipertensi_actual_name = None
    for f in actual_files:
        if f.startswith("Bahaya Hipertensi"):
            hipertensi_actual_name = f
            break

    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("⏳ Memulai proses ekstraksi dan embedding PDF via Google Native SDK...")
    
    for file_name, category in PDF_MAPPING.items():
        target_file = file_name
        if file_name.startswith("Bahaya Hipertensi") and hipertensi_actual_name:
            target_file = hipertensi_actual_name

        file_path = os.path.join(pdf_dir, target_file)
        
        if not os.path.exists(file_path):
            print(f"⚠️ File tidak ditemukan, skip: {target_file}")
            continue
            
        print(f"📖 Melakukan parsing file: {target_file} ({category})")
        
        reader = PdfReader(file_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
                
        chunks = split_text_into_chunks(full_text)
        print(f"✂️ Berhasil memotong teks menjadi {len(chunks)} chunks.")
        
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            
            try:
                result = genai.embed_content(
                    model="models/gemini-embedding-2",
                    content=chunk.strip(),
                    task_type="retrieval_document"
                )
                vector = result['embedding']
                
                query = """
                    INSERT INTO medical_knowledge (category, source_file, content, embedding)
                    VALUES (%s, %s, %s, %s);
                """
                cursor.execute(query, (category, target_file, chunk.strip(), vector))
                conn.commit() # Commit per baris biar aman
                
            except Exception as api_error:
                print(f"❌ Error pas embedding chunk ke-{idx}: {str(api_error)}")
                conn.rollback() # <--- PERBAIKAN: Reset status transaksi biar SQL gak mogok kerja lagi
                continue
            
        print(f"✅ Kategori {category} selesai dimasukkan ke database!")
        
    cursor.close()
    conn.close()
    print("\n🚀 PROSES INGESTION BERHASIL! Database RAG lo sekarang sudah terisi penuh 3072 Dimensi!")
        
    cursor.close()
    conn.close()
    print("\n🚀 PROSES INGESTION BERHASIL! Database RAG lo sekarang sudah terisi penuh.")

if __name__ == "__main__":
    ingest_all_pdfs()