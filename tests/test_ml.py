import pytest

from app.core.config import get_settings
from ml.factory import get_predictor
from ml.interface import PredictInput, PredictOutput
from ml.real import RealPredictor
from ml.stub import StubPredictor


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_stub_output_shape_and_determinism():
    p = StubPredictor()
    a = p.predict(PredictInput(text="hello"))
    assert isinstance(a, PredictOutput)
    assert 0 <= a.score <= 1
    assert a == p.predict(PredictInput(text="hello"))


def test_factory_stub(monkeypatch):
    monkeypatch.setenv("ML_BACKEND", "stub")
    assert isinstance(get_predictor(), StubPredictor)


def test_factory_real(monkeypatch):
    monkeypatch.setenv("ML_BACKEND", "real")
    predictor = get_predictor()
    assert isinstance(predictor, RealPredictor)
    with pytest.raises(NotImplementedError):
        predictor.predict(PredictInput(text="x"))


def test_factory_unknown(monkeypatch):
    monkeypatch.setenv("ML_BACKEND", "nope")
    with pytest.raises(ValueError):
        get_predictor()


async def test_predict_endpoint(client):
    r = await client.post("/predict", json={"text": "hello"})
    assert r.status_code == 200
    assert set(r.json()) == {"label", "score"}
