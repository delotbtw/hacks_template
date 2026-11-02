from app.core.config import get_settings
from ml.interface import Predictor
from ml.real import RealPredictor
from ml.stub import StubPredictor


def get_predictor() -> Predictor:
    backend = get_settings().ml_backend
    if backend == "stub":
        return StubPredictor()
    if backend == "real":
        return RealPredictor()
    raise ValueError(f"Неизвестный ML_BACKEND={backend!r}: допустимо stub|real")
