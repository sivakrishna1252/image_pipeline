import logging
from io import BytesIO
from PIL import Image
from app.config import Config
logger = logging.getLogger(__name__)


class ImageValidator:
    @staticmethod
    def validate(file) -> tuple[bool, str, bytes, tuple[int, int]]:
       

        if hasattr(file, "read"):
            raw_bytes: bytes = file.read()
            if hasattr(file, "seek"):
                file.seek(0)
        elif isinstance(file, (bytes, bytearray)):
            raw_bytes = bytes(file)
        else:
            return False, "Cannot read file data", b"", (0, 0)

        filename: str = getattr(file, "filename", "") or ""
        if filename:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext not in Config.ALLOWED_EXTENSIONS:
                msg = (
                    f"Invalid file format '.{ext}'. "
                    f"Allowed: {', '.join(sorted(Config.ALLOWED_EXTENSIONS))}"
                )
                logger.warning("Rejected file '%s': %s", filename, msg)
                return False, msg, b"", (0, 0)

        size_bytes = len(raw_bytes)
        size_kb    = size_bytes / 1024
        size_mb    = size_bytes / (1024 * 1024)

        logger.info(
            "Received file '%s' → size=%.2f KB (%.4f MB)",
            filename, size_kb, size_mb,
        )

        if size_bytes > Config.MAX_FILE_SIZE:
            msg = (
                f"File size {size_mb:.2f} MB exceeds the 2 MB limit. "
                "Please upload a smaller image."
            )
            logger.warning("Rejected file '%s': %s", filename, msg)
            return False, msg, b"", (0, 0)

        try:
            with Image.open(BytesIO(raw_bytes)) as img:
                img.verify()           

            with Image.open(BytesIO(raw_bytes)) as img:
                width, height = img.size

        except Exception as exc:
            msg = f"Cannot read image file: {exc}"
            logger.warning("Rejected file '%s': %s", filename, msg)
            return False, msg, b"", (0, 0)

        logger.info(
            "Validated file '%s' → %d×%d px, %.2f KB",
            filename, width, height, size_kb,
        )
        return True, "", raw_bytes, (width, height)
