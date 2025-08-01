from urllib.parse import urlparse

from flask import flash
from validators import url as validate_url


def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def validate(url):
    if not url:
        flash("URL обязателен", "danger")
        return False

    if len(url) > 255:
        flash("URL превышает 255 символов", "danger")
        return False

    if not validate_url(url):
        flash("Некорректный URL", "danger")
        return False

    return True
