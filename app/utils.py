# app/utils.py
import shortuuid
from app.config import settings

def generate_short_code() -> str:
    """
    Generates a unique short code using shortuuid.
    The length is configurable via settings.
    """
    return shortuuid.uuid()[:settings.SHORT_CODE_LENGTH]

