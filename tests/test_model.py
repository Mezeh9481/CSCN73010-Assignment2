"""Image preparation and prediction logic."""

from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image

import model


def test_preprocess_converts_grayscale_to_normalized_rgb():
    """Grayscale uploads acquire three channels and normalized pixels."""
    source = BytesIO()
    Image.new("L", (5, 3), 128).save(source, format="PNG")
    source.seek(0)

    result = model.preprocess_img(source)

    assert result.shape == (1, 224, 224, 3)
    assert result.dtype == np.float32
    assert np.allclose(result, 128 / 255.0)


def test_predict_result_returns_highest_score(monkeypatch):
    """Class selection uses the highest model score."""
    class FakeModel:  # pylint: disable=too-few-public-methods
        """Minimal model double."""

        def predict(self, batch, verbose=0):
            """Return deterministic class scores."""
            assert batch.shape == (1, 224, 224, 3)
            assert verbose == 0
            return np.array([[0.1, 0.7, 0.2]])

    monkeypatch.setattr(model, "get_model", FakeModel)
    digit = model.predict_result(np.zeros((1, 224, 224, 3)))

    assert digit == 1
    assert isinstance(digit, int)


def test_bundled_model_predicts_sample():
    """The repository model loads and returns one of its ten digit classes."""
    sample = Path(__file__).resolve().parents[1] / "test_images" / "2" / "Sign 2 (115).jpeg"
    prediction = model.predict_result(model.preprocess_img(sample))
    assert 0 <= prediction <= 9
