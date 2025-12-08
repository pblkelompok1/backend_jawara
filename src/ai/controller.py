from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from src.exceptions import AppException
from src.ai.service import save_upload_file, predict_from_file
from src.ai.schemas import PredictResponse, PredictionResult
import os

router = APIRouter(prefix="/ai", tags=["AI Service"])

# Pemetaan deskripsi dan gambar serupa berdasarkan label
label_to_description = {
    "bunga_kol": {
        "description": "Bunga kol adalah sayuran yang kaya akan vitamin C, serat, dan antioksidan. Baik untuk kesehatan pencernaan dan sistem kekebalan tubuh.",
        "scientific_name": "Brassica oleracea var. botrytis",
        "similar_images": [
            "/storage/vegetable_images/bunga_kol/bunga_kol_1.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_2.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_3.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_4.jpg",
            "/storage/vegetable_images/bunga_kol/bunga_kol_5.jpg",
        ] 
    },
    "cabai": {
        "description": "Cabai adalah sayuran pedas yang sering digunakan dalam masakan untuk memberikan rasa pedas dan mengandung capsaicin yang bermanfaat untuk kesehatan.",
        "scientific_name": "Capsicum annuum",
        "similar_images": [
            "/storage/vegetable_images/cabai/cabai_1.jpg",
            "/storage/vegetable_images/cabai/cabai_2.jpg",
            "/storage/vegetable_images/cabai/cabai_3.jpg",
            "/storage/vegetable_images/cabai/cabai_4.jpg",
            "/storage/vegetable_images/cabai/cabai_5.jpg",
        ]
    },
    "kubis": {
        "description": "Kubis adalah sayuran yang kaya akan serat, vitamin K, dan vitamin C. Sering digunakan dalam salad dan masakan fermentasi.",
        "scientific_name": "Brassica oleracea var. capitata",
        "similar_images": [
            "/storage/vegetable_images/kubis/kubis_1.jpg",
            "/storage/vegetable_images/kubis/kubis_2.jpg",
            "/storage/vegetable_images/kubis/kubis_3.jpg",
            "/storage/vegetable_images/kubis/kubis_4.jpg",
            "/storage/vegetable_images/kubis/kubis_5.jpg",
        ]
    },
    "sawi_hijau": {
        "description": "Sawi hijau adalah sayuran berdaun hijau yang kaya akan vitamin A, C, dan K. Baik untuk kesehatan mata dan tulang.",
        "scientific_name": "Brassica rapa var. parachinensis",
        "similar_images": [
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_1.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_2.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_3.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_4.jpg",
            "/storage/vegetable_images/sawi_hijau/sawi_hijau_5.jpg",
        ]
    },
    "sawi_putih": {
        "description": "Sawi putih memiliki rasa ringan dan tekstur renyah. Kaya akan vitamin C dan folat, sering digunakan dalam masakan Asia.",
        "scientific_name": "Brassica rapa var. pekinensis",
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
        scientific_name = label_to_description.get(label, {}).get("scientific_name", "")
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

    # Mengembalikan respons termasuk label, confidence, deskripsi, nama ilmiah, dan gambar serupa
    return PredictResponse(
        success=True,
        result=PredictionResult(
            label=label,
            confidence=confidence,
            description=description,
            scientific_name=scientific_name,
            similar_images=similar_images
        )
    )
