from pydantic import BaseModel


class TrainResponse(BaseModel):
    r2: float
    mae: float
    rmse: float
    samples: list[dict]
    feature_importance: list[dict]
    error_by_range: dict[str, float]
    train_size: int
    test_size: int


class PredictRequest(BaseModel):
    place: str
    room_count: int = 3
    avg_area: float = 100.0
    property_type: str = "住宅"


class PredictResponse(BaseModel):
    predicted_price: float
    confidence_interval: list[float]
    features: dict
