from typing import Tuple
import cv2
import numpy as np
from skimage.feature import hog, local_binary_pattern
from src.exceptions import AppException
from src.ai.model_loader import load_model
import os
import secrets
from sklearn.preprocessing import LabelEncoder

# LabelEncoder untuk memetakan index ke label
le = LabelEncoder()
le.fit(["bunga_kol", "cabai", "kubis", "sawi_hijau", "sawi_putih"])

# --------------------------
# SEGMENTASI GRABCUT
# --------------------------
def segment_grabcut(img: np.ndarray) -> np.ndarray:
    mask = np.zeros(img.shape[:2], np.uint8)

    h, w = img.shape[:2]
    rect = (int(w * 0.15), int(h * 0.15), int(w * 0.7), int(h * 0.7))  # Lebih ketat

    bgModel = np.zeros((1, 65), np.float64)
    fgModel = np.zeros((1, 65), np.float64)

    cv2.grabCut(img, mask, rect, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")

    # Perbaiki tepi dengan morphological closing
    kernel = np.ones((5, 5), np.uint8)
    mask2 = cv2.morphologyEx(mask2, cv2.MORPH_CLOSE, kernel)

    return img * mask2[:, :, np.newaxis]


# ---------------------------
# EKSTRAKSI FITUR HOG
# ---------------------------
def extract_hog_features(img: np.ndarray) -> np.ndarray:
    # Konversi ke grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize agar konsisten (opsional)
    gray = cv2.resize(gray, (128, 128))

    # Ekstraksi HOG
    hog_features = hog(
        gray,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm='L2-Hys',
        visualize=False,
        transform_sqrt=True
    )
    return hog_features


# ---------------------------
# EKSTRAKSI FITUR LBP
# ---------------------------
def extract_lbp_features(img: np.ndarray, P=8, R=1) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (128, 128))  # Resize untuk konsistensi ukuran

    # Hitung LBP
    lbp = local_binary_pattern(gray, P, R, method="uniform")

    # Hitung histogram LBP (jumlah bin = P+2)
    (hist, _) = np.histogram(
        lbp.ravel(),
        bins=np.arange(0, P + 3),
        range=(0, P + 2)
    )

    # Normalisasi histogram
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)  # Normalisasi histogram
    return hist


# ---------------------------
# GABUNGKAN FITUR HOG & LBP
# ---------------------------
def extract_features(img: np.ndarray) -> np.ndarray:
    # Terapkan segmentasi terlebih dahulu (dengan GrabCut)
    img_segmented = segment_grabcut(img)

    # Ekstraksi HOG dan LBP
    hog_feat = extract_hog_features(img_segmented)
    lbp_feat = extract_lbp_features(img_segmented)

    # Gabungkan kedua fitur menjadi satu vektor
    feature_vector = np.hstack([hog_feat, lbp_feat])
    return feature_vector


# ---------------------------
# PREDIKSI DARI FILE
# ---------------------------
def predict_from_file(file_path: str) -> Tuple[str, float]:
    """
    Mengambil file path gambar (yang sudah disimpan), lakukan preprocess, ekstraksi fitur,
    dan prediksi menggunakan model pipeline yang sudah di-load.
    Return (label, confidence)
    """
    # Membaca gambar
    img = cv2.imread(file_path)
    if img is None:
        raise AppException("Gagal membaca file gambar.")

    # Ekstraksi fitur dari gambar
    features = extract_features(img).reshape(1, -1)

    # Memuat model
    model = load_model()

    try:
        # Prediksi kelas (model mengembalikan angka)
        pred = model.predict(features)[0]

        # Mengonversi angka ke nama label menggunakan LabelEncoder
        label = le.inverse_transform([int(pred)])[0]  # Mengonversi angka ke nama label

        # Menghitung confidence jika model mendukung predict_proba()
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(features)[0]
            confidence = float(np.max(proba))
        else:
            confidence = 1.0
    except Exception as e:
        raise AppException(f"Gagal melakukan prediksi: {e}")

    return label, confidence


# ---------------------------
# SIMPAN FILE UPLOAD
# ---------------------------
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "storage", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_upload_file(upload_file) -> str:
    """
    Simpan file UploadFile FastAPI ke disk dan kembalikan path file yang disimpan.
    Menggunakan nama file acak untuk menghindari bentrok nama file.
    """
    # Buat nama file acak untuk menghindari bentrok
    filename = secrets.token_hex(12) + "_" + upload_file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(upload_file.file.read())  # Simpan file
    except Exception as e:
        raise AppException(f"Gagal menyimpan file upload: {e}")
    
    return file_path
