from io import BytesIO
from PIL import Image
from numpy import ndarray, asarray, uint8


class ImageTransformer:
    @staticmethod
    def transform_image(image: bytes, image_edge: int) -> ndarray:
        image = BytesIO(image)
        image = Image.open(image)
        image = image.resize((image_edge, image_edge), resample=Image.ANTIALIAS)
        image = asarray(image, dtype=uint8).reshape(image_edge, image_edge, 1)
        image = image / 255.
        return image
