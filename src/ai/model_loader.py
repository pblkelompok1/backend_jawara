import os
import joblib
from src.exceptions import AppException

MODEL_FILENAME = "model_sayur.pkl"  # Gantilah dengan nama file model Anda
MODEL_PATH = os.path.join(os.path.dirname(__file__), MODEL_FILENAME)

_model = None

def load_model():
    """
    Fungsi untuk memuat model sekali saja. 
    Raise AppException jika model gagal dimuat.
    """
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise AppException(f"Model file not found: {MODEL_PATH}")
        try:
            _model = joblib.load(MODEL_PATH)  
        except Exception as e:
            raise AppException(f"Failed to load model: {e}")
    return _model
