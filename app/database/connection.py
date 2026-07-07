# app/database/connection.py
import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import settings
import time

def get_db_connection():
    """
    Fungsi untuk membuka koneksi ke database PostgreSQL secara dinamis.
    Menggunakan RealDictCursor agar hasil query SQL otomatis jadi Python Dictionary (JSON-ready).
    """
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursor_factory=RealDictCursor # Mengubah baris tabel jadi dict otomatis
        )
        return conn
    except Exception as e:
        print(f"❌ Gagal koneksi ke PostgreSQL: {str(e)}")
        raise e