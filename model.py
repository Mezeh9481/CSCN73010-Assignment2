"""Image preparation and hand-sign digit prediction."""

from functools import lru_cache
from importlib import import_module
from pathlib import Path

import numpy as np
from PIL import Image

MODEL_PATH = Path(__file__).resolve().with_name("digit_model.h5")
IMAGE_SIZE = (224, 224)


def preprocess_img(image_source):
    """Return an RGB image as a normalized batch with shape (1, 224, 224, 3)."""
    with Image.open(image_source) as image:
        rgb_image = image.convert("RGB")
        resized_image = rgb_image.resize(IMAGE_SIZE)
        pixels = np.asarray(resized_image, dtype=np.float32) / 255.0
    return np.expand_dims(pixels, axis=0)


@lru_cache(maxsize=1)
def get_model():
    """Load the bundled model on first prediction and reuse it thereafter."""
    layers = import_module("keras.layers")

    class LegacyDepthwiseConv2D(layers.DepthwiseConv2D):  # pylint: disable=too-few-public-methods
        """Ignore an obsolete Keras argument stored in the bundled model."""

        def __init__(self, *args, **kwargs):
            kwargs.pop("groups", None)
            super().__init__(*args, **kwargs)

    return import_module("keras.models").load_model(
        MODEL_PATH,
        compile=False,
        custom_objects={"DepthwiseConv2D": LegacyDepthwiseConv2D},
    )


def predict_result(image_batch):
    """Return the index of the highest-scoring digit class."""
    scores = get_model().predict(image_batch, verbose=0)
    return int(np.argmax(scores[0]))
