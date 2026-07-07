# ml_model/train_real_model.py
import os
import sys
import pickle
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import settings

def train_mature_catboost_model():
    raw_path = settings.DATASET_PATH
    dataset_path = os.path.join("..", raw_path) if not os.path.isabs(raw_path) else raw_path
    
    if not os.path.exists(dataset_path):
        print(f"❌ File dataset gak ketemu di: {dataset_path}")
        return

    print(f"📖 Membaca dataset BRFSS asli dari konfig: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # =========================================================================
    # BENTENG ANTI-GIGO 1: DATA CLEANING & OUTLIER HANDLING (Paling Optimal)
    # =========================================================================
    # 1. Drop data kosong jika ada, biar gak bikin error matriks linear CatBoost
    df = df.dropna(subset=['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker', 'Diabetes_binary'])
    
    # 2. Filter Outlier Medis Ekstrem pada BMI (Berdasarkan batas Pydantic API kita)
    # Sesuai standar klinis, BMI manusia hidup sangat jarang di bawah 10 atau di atas 70
    df = df[(df['BMI'] >= 10.0) & (df['BMI'] <= 70.0)]
    
    features = ['Age', 'Sex', 'BMI', 'HighBP', 'HighChol', 'Smoker']
    target = 'Diabetes_binary'
    
    cat_features_indices = [0, 1, 3, 4, 5]
    for col_idx in cat_features_indices:
        df[features[col_idx]] = df[features[col_idx]].astype(int)
        
    X = df[features]
    y = df[target].astype(int)
    
    # =========================================================================
    # BENTENG ANTI-GIGO 2: STRATIFIED SPLITTING (Menjaga Distribusi Target)
    # =========================================================================
    # Tambahkan parameter stratify=y biar proporsi 50:50 terjaga ketat di Train & Test set!
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.2, 
        stratify=y, # <--- KUNCI UTAMA SAMPLING OPTIMAL
        random_state=42
    )
    
    print(f"✅ Data bersih terverifikasi. Jumlah baris training: {len(X_train)}")
    print("\n⚙️ Memulai Hyperparameter Tuning via NATIVE CatBoost Grid Search...")
    model = CatBoostClassifier(loss_function='Logloss', verbose=0, random_seed=42)
    
    param_grid = {
        'iterations': [300, 500],
        'learning_rate': [0.03, 0.1],
        'depth': [4, 6],
        'l2_leaf_reg': [3, 5]
    }
    
    model.grid_search(param_grid, X=X_train, y=y_train, cv=3, verbose=False)
    
    print("\n🏆 HYPERPARAMETER TERBAIK YANG DITEMUKAN:")
    print(model.get_params())
    
    # Evaluasi Performa
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    print("\n📊 HASIL EVALUASI MODEL CATBOOST TEROPTIMAL:")
    print(f"Accuracy Score : {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print(f"ROC-AUC Score  : {roc_auc_score(y_test, y_prob) * 100:.2f}%")
    
    # Simpan Model Terbaik ke folder weights
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    weights_dir = os.path.abspath(os.path.join(BASE_DIR, "..", "app", "services", "weights"))
    os.makedirs(weights_dir, exist_ok=True)
    model_path = os.path.join(weights_dir, "mock_ptm_model.pkl")
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
        
    print(f"🎯 MODEL CATBOOST MATANG BERHASIL DISIMPAN DI: {model_path}")

if __name__ == "__main__":
    train_mature_catboost_model()