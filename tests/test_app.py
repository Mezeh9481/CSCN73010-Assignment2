"""HTTP behavior for upload and prediction routes."""

from io import BytesIO

from PIL import Image

import app


def make_image(mode="RGB", color=(255, 0, 0)):
    """Return a small valid PNG image in memory."""
    image = Image.new(mode, (12, 8), color)
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output


def test_home_page(client):
    """The upload page is available."""
    response = client.get("/")
    assert response.status_code == 200
    assert b'name="file"' in response.data


def test_valid_image_returns_prediction(client, monkeypatch):
    """A real image passes preprocessing and a fake model result is displayed."""
    observed = {}

    def fake_predict(image_batch):
        observed["shape"] = image_batch.shape
        return 4

    monkeypatch.setattr(app, "predict_result", fake_predict)
    response = client.post(
        "/prediction",
        data={"file": (make_image(), "hand.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    assert b">4</h2>" in response.data
    assert observed["shape"] == (1, 224, 224, 3)


def test_missing_file_is_rejected(client):
    """A request without a file returns a clear client error."""
    response = client.post("/prediction", data={})
    assert response.status_code == 400
    assert b"Please choose an image file." in response.data


def test_empty_filename_is_rejected(client):
    """An empty filename is treated as no selection."""
    response = client.post(
        "/prediction",
        data={"file": (make_image(), "")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400


def test_invalid_image_is_rejected(client):
    """Bytes that are not an image do not reach the model."""
    response = client.post(
        "/prediction",
        data={"file": (BytesIO(b"not an image"), "bad.png")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    assert b"File cannot be processed." in response.data


def test_prediction_requires_post(client):
    """The prediction route does not accept GET requests."""
    assert client.get("/prediction").status_code == 405
