from pydantic import BaseModel
from typing import List, Optional

class PredictionResult(BaseModel):
    label: str
    confidence: float
    description: Optional[str] = None  
    similar_images: Optional[List[str]] = []

class PredictResponse(BaseModel):
    success: bool
    result: Optional[PredictionResult] = None
    message: Optional[str] = None
