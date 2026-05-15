from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ml import PredictRequest, PredictResponse, TrainResponse
from app.services import ml_service

router = APIRouter(prefix="/api/ml", tags=["ml"])


@router.post("/train", response_model=TrainResponse)
def train_model(db: Session = Depends(get_db)):
    try:
        return ml_service.train(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}",
        )


@router.post("/predict", response_model=PredictResponse)
def predict_price(data: PredictRequest):
    result = ml_service.predict(data.model_dump())
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model not trained yet. Please call /api/ml/train first.",
        )
    return result
