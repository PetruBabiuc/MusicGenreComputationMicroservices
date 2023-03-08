import base64


def bytes_to_string(b: bytes) -> str:
    return base64.b64encode(b).decode()


def string_to_bytes(s: str) -> bytes:
    return base64.b64decode(s)
