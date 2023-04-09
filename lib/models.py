from easyocr import Reader


def create_model(languages=["en"]) -> Reader:
    return Reader(languages)
