import logging
import os
from io import BytesIO
from PIL import Image
from app.config import Config
logger = logging.getLogger(__name__)


class MediaValidator:
    @staticmethod
    def validate(file) -> tuple[bool, str, bytes, tuple[int, int], str]:
        """
        Validates images and videos.
        Returns: (bool, error_msg, raw_bytes, dimensions, media_type)
        media_type is either 'IMAGE' or 'VIDEO'.
        """
       
        if hasattr(file, "read"):
            raw_bytes: bytes = file.read()
            if hasattr(file, "seek"):
                file.seek(0)
        elif isinstance(file, (bytes, bytearray)):
            raw_bytes = bytes(file)
        else:
            return False, "Cannot read file data", b"", (0, 0), ""

        filename: str = getattr(file, "filename", "") or ""
        ext = ""
        if filename:
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext not in Config.ALLOWED_EXTENSIONS:
                msg = (
                    f"Invalid file format '.{ext}'. "
                    f"Allowed: {', '.join(sorted(Config.ALLOWED_EXTENSIONS))}"
                )
                logger.warning("Rejected file '%s': %s", filename, msg)
                return False, msg, b"", (0, 0), ""

        size_bytes = len(raw_bytes)
        size_kb    = size_bytes / 1024
        size_mb    = size_bytes / (1024 * 1024)

        logger.info(
            "Received file '%s' → size=%.2f KB (%.4f MB)",
            filename, size_kb, size_mb,
        )

        if size_bytes > Config.MAX_FILE_SIZE:
            msg = f"File size {size_mb:.2f} MB exceeds the limit."
            logger.warning("Rejected file '%s': %s", filename, msg)
            return False, msg, b"", (0, 0), ""

        is_video = ext in Config.ALLOWED_VIDEO_EXTENSIONS
        media_type = "VIDEO" if is_video else "IMAGE"
        width, height = (0, 0)

        if not is_video:
            try:
                with Image.open(BytesIO(raw_bytes)) as img:
                    img.verify()           
                with Image.open(BytesIO(raw_bytes)) as img:
                    width, height = img.size
            except Exception as exc:
                msg = f"Cannot read image file: {exc}"
                logger.warning("Rejected file '%s': %s", filename, msg)
                return False, msg, b"", (0, 0), ""
        else:
            # Video validation can be more complex (e.g., checking if ffmpeg can read it)
            # For now, we rely on extension and size.
            logger.info("Video detected: %s", filename)
            pass

        logger.info(
            "Validated %s file '%s' → %s px, %.2f KB",
            media_type, filename, f"{width}x{height}" if not is_video else "N/A", size_kb,
        )
        return True, "", raw_bytes, (width, height), media_type
