from fastapi import APIRouter

from ml.factory import get_predictor
from ml.interface import PredictInput, PredictOutput

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictOutput)
async def predict(data: PredictInput):
    return get_predictor().predict(data)
