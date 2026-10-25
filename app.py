"""Flask routes for hand-sign digit recognition."""

from flask import Flask, render_template, request
from PIL import UnidentifiedImageError

from model import predict_result, preprocess_img

app = Flask(__name__)


@app.get("/")
def main():
    """Render the image upload page."""
    return render_template("index.html")


@app.post("/prediction")
def predict_image_file():
    """Validate an uploaded image and display its predicted digit."""
    uploaded_file = request.files.get("file")
    if uploaded_file is None or not uploaded_file.filename:
        return render_template(
            "result.html", err="Please choose an image file."
        ), 400

    try:
        image_batch = preprocess_img(uploaded_file.stream)
    except (UnidentifiedImageError, OSError, ValueError):
        return render_template(
            "result.html", err="File cannot be processed."
        ), 400

    prediction = predict_result(image_batch)
    return render_template("result.html", predictions=str(prediction))


if __name__ == "__main__":
    app.run(port=9000)
