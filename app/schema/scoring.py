# app/schemas/scoring.py
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class HealthQuizInput(BaseModel):
    # Batasi umur manusia yang logis untuk diabetes tipe 2 (misal 1-120 tahun)
    age: int = Field(..., description="Umur pasien dalam satuan tahun", ge=1, le=120)
    
    # Kunci pilihan gender hanya boleh MALE atau FEMALE (Anti typo/garbage text)
    gender: Literal["MALE", "FEMALE"] = Field(..., description="Jenis kelamin pasien")
    
    # Batasi BMI berdasarkan rekor klinis manusia (BMI terendah/tertinggi ekstrem)
    bmi: float = Field(..., description="Body Mass Index pasien (kg/m^2)", ge=10.0, le=70.0)
    
    # Input riwayat kesehatan wajib bertipe boolean (True/False atau 1/0)
    high_bp: bool = Field(..., description="Apakah memiliki riwayat tekanan darah tinggi?")
    high_chol: bool = Field(..., description="Apakah memiliki riwayat kolesterol tinggi?")
    smoker: bool = Field(..., description="Apakah perokok aktif?")

    # Custom Validator: Contoh pencegahan logika sampah
    @field_validator('bmi')
    @classmethod
    def validate_bmi_logic(cls, v: float) -> float:
        # Jika ada user iseng masukin angka yang tipis banget atau gak masuk akal
        if v == 0.0:
            raise ValueError("BMI tidak boleh berangka nol, bro!")
        return round(v, 2) # Otomatis merapikan desimal bising