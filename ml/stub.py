from ml.interface import PredictInput, PredictOutput


class StubPredictor:
    """Детерминированная заглушка: ответ зависит только от длины текста."""

    def predict(self, data: PredictInput) -> PredictOutput:
        positive = len(data.text) % 2 == 0
        return PredictOutput(
            label="positive" if positive else "negative", score=0.75 if positive else 0.25
        )
