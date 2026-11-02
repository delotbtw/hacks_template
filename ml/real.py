from ml.interface import PredictInput, PredictOutput


class RealPredictor:
    """Настоящая модель. Реализуйте после обучения (см. ml/train.py)."""

    def predict(self, data: PredictInput) -> PredictOutput:
        raise NotImplementedError(
            "RealPredictor не реализован: обучите модель в ml/train.py (сохраните в models/), "
            "загрузите её в __init__ и верните PredictOutput. Пока используйте ML_BACKEND=stub."
        )
