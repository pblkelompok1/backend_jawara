from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from src.exceptions import AppException
from src.ai.service import save_upload_file, predict_from_file
from src.ai.schemas import PredictResponse, PredictionResult
import os

router = APIRouter(prefix="/ai", tags=["AI Service"])

# Pemetaan deskripsi dan gambar serupa berdasarkan label
label_to_description = {
    "bunga_kol": {
        "description": "Brokoli adalah sayuran hijau yang mengandung banyak vitamin C, serat, antioksidan, dan baik untuk kesehatan.",
        "similar_images": [
            "/storage/vegetable_images/bunga_kol/bunga_kol_1.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_2.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_3.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_4.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_5.jpg",
        ] 
    },
    "cabai": {
        "description": "Cabai adalah sayuran pedas yang sering digunakan dalam masakan untuk memberikan rasa pedas.",
        "similar_images": [
            "/storage/vegetable_images/cabai/cabai_1.jpg",
            "/storage/vegetable_images/cabai/cabai_2.jpg",
            "/storage/vegetable_images/cabai/cabai_3.jpg",
            "/storage/vegetable_images/cabai/cabai_4.jpg",
            "/storage/vegetable_images/cabai/cabai_5.jpg",
        ]
    },
    "kubis": {
        "description": "Kubis adalah sayuran yang kaya akan serat dan vitamin K, sering digunakan dalam salad dan masakan.",
        "similar_images": [
            "/storage/vegetable_images/kubis/kubis_1.jpg",
            "/storage/vegetable_images/kubis/kubis_2.jpg",
            "/storage/vegetable_images/kubis/kubis_3.jpg",
            "/storage/vegetable_images/kubis/kubis_4.jpg",
            "/storage/vegetable_images/kubis/kubis_5.jpg",
        ]
    },
    "sawi_hijau": {
        "description": "Sawi hijau adalah sayuran berdaun hijau yang kaya akan vitamin A dan C, baik untuk kesehatan mata.",
        "similar_images": [
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_1.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_2.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_3.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_4.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_5.jpg",
        ]
    },
    "sawi_putih": {
        "description": "Sawi putih memiliki rasa ringan dan tekstur renyah, sering digunakan dalam masakan Asia.",
        "similar_images": [
            "/storage/vegetable_images/sawi_putih/sawi_putih_1.jpg",
            "/storage/vegetable_images/sawi_putih/sawi_putih_2.jpg",
            "/storage/vegetable_images/sawi_putih/sawi_putih_3.jpg",
            "/storage/vegetable_images/sawi_putih/sawi_putih_4.jpg",
            "/storage/vegetable_images/sawi_putih/sawi_putih_5.jpg",
        ]
    },

}

@router.post("/predict", response_model=PredictResponse)
async def predict_image_endpoint(image: UploadFile = File(...)):
    # Simpan file sementara
    try:
        saved_path = save_upload_file(image)
    except AppException as ae:
        raise HTTPException(status_code=400, detail=str(ae))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    # Lakukan prediksi
    try:
        label, confidence = predict_from_file(saved_path)

        # Mengambil deskripsi dan gambar serupa berdasarkan label yang diprediksi
        description = label_to_description.get(label, {}).get("description", "")
        similar_images = label_to_description.get(label, {}).get("similar_images", [])

    except AppException as ae:
        # Bersihkan file dan kembalikan error
        try:
            os.remove(saved_path)
        except Exception:
            pass
        raise HTTPException(status_code=400, detail=str(ae))
    except Exception as e:
        try:
            os.remove(saved_path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"Internal prediction error: {e}")

    # Hapus file sementara (opsional)
    try:
        os.remove(saved_path)
    except Exception:
        pass

    # Mengembalikan respons termasuk label, confidence, deskripsi, dan gambar serupa
    return PredictResponse(
        success=True,
        result=PredictionResult(
            label=label,
            confidence=confidence,
            description=description,
            similar_images=similar_images
        )
    )
