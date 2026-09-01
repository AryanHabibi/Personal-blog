import uuid
from pathlib import Path

from fastapi import UploadFile

# api/uploads/ - resolved from this file, so it does not depend on the cwd.
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
MAX_IMAGE_BYTES = 5 * 1024 * 1024
_EXT_BY_TYPE = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class ImageError(ValueError):
    """Bad upload - the router turns this into a 422."""


def save_image(file: UploadFile) -> tuple[str, str]:
    """Persist an uploaded image and return (stored_filename, content_type)."""
    content_type = (file.content_type or "").lower()
    if content_type not in _EXT_BY_TYPE:
        raise ImageError("Image must be JPEG, PNG, or WebP")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{_EXT_BY_TYPE[content_type]}"
    dest = UPLOAD_DIR / filename

    size = 0
    try:
        with dest.open("wb") as out:
            while chunk := file.file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_IMAGE_BYTES:
                    raise ImageError("Image exceeds the 5 MB limit")
                out.write(chunk)
    except ImageError:
        dest.unlink(missing_ok=True)
        raise
    finally:
        file.file.close()

    if size == 0:
        dest.unlink(missing_ok=True)
        raise ImageError("Image file is empty")
    return filename, content_type


def delete_image(filename: str | None) -> None:
    if filename:
        (UPLOAD_DIR / filename).unlink(missing_ok=True)


def image_path(filename: str) -> Path:
    return UPLOAD_DIR / filename
