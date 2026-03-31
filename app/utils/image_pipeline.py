import logging
import os
import tempfile
import subprocess
from io import BytesIO
from PIL import Image
from app.config import Config

logger = logging.getLogger(__name__)

_TARGET_MAX: int = Config.TARGET_MAX_BYTES
_TARGET_MIN: int = Config.TARGET_MIN_BYTES
_QUALITY_FLOOR: int = Config.QUALITY_FLOOR
_QUALITY_MAX:   int = Config.QUALITY_MAX
_QUALITY_AFTER_RESIZE: int = 70
_QUALITY_STEP: int = 5

_RESOLUTION_RULES: list[tuple[float, float, int | None]] = [
    (8.0,  float("inf"), 1600),   
    (4.0,  8.0,          1400),  
    (2.0,  4.0,          1200),   
    (1.0,  2.0,          1000),   
    (0.0,  1.0,          None), 
]

_SIZE_QUALITY_MAP: list[tuple[int, int, int]] = [
    (int(1.5  * 1024 * 1024), int(2.0 * 1024 * 1024), 55),
    (int(1.0  * 1024 * 1024), int(1.5 * 1024 * 1024), 60),
    (int(500  * 1024),        int(1.0 * 1024 * 1024), 70),
    (int(300  * 1024),        int(500 * 1024),         75),
    (0,                       int(300 * 1024),         80),
]

def _get_initial_quality(original_size: int) -> int:
    for min_b, max_b, quality in _SIZE_QUALITY_MAP:
        if min_b <= original_size < max_b:
            return quality
    return 70

def _get_max_dimension(width: int, height: int) -> int | None:
    mp = (width * height) / 1_000_000
    for min_mp, max_mp, max_dim in _RESOLUTION_RULES:
        if min_mp <= mp < max_mp:
            return max_dim
    return None

def _resize_to_max(img: Image.Image, max_dim: int) -> Image.Image:
    w, h = img.size
    if max(w, h) <= max_dim:
        return img

    if w >= h:
        new_w = max_dim
        new_h = max(1, int(h * max_dim / w))
    else:
        new_h = max_dim
        new_w = max(1, int(w * max_dim / h))

    logger.info("  Resolution resize → %dx%d → %dx%d", w, h, new_w, new_h)
    return img.resize((new_w, new_h), Image.LANCZOS)

def _encode_webp(img: Image.Image, quality: int) -> bytes:
    buf = BytesIO()
    img.save(buf, format="WEBP", quality=quality, method=6)
    return buf.getvalue()

def compress_to_webp(raw_bytes: bytes, dimensions: tuple[int, int]) -> tuple[bytes, dict]:
    original_size = len(raw_bytes)
    original_kb   = original_size / 1024
    width, height = dimensions
    logger.info("Compression START | original=%.2f KB | %dx%d", original_kb, width, height)
    img: Image.Image = Image.open(BytesIO(raw_bytes))
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGBA")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    mp = (width * height) / 1_000_000
    max_dim = _get_max_dimension(width, height)

    if max_dim is not None:
        logger.info("  Resolution Cap → %.2f MP → max_dim=%d px", mp, max_dim)
        img = _resize_to_max(img, max_dim)
    else:
        logger.info("  Resolution Cap → %.2f MP → keep original", mp)

    current_img = img
    quality = _get_initial_quality(original_size)
    logger.info("  Quality Map → initial quality=%d", quality)
    best_bytes = _encode_webp(current_img, quality)

    while len(best_bytes) >= _TARGET_MAX:
        quality -= _QUALITY_STEP
        if quality < _QUALITY_FLOOR:
            w, h = current_img.size
            new_w, new_h = max(1, int(w * 0.90)), max(1, int(h * 0.90))
            current_img = current_img.resize((new_w, new_h), Image.LANCZOS)
            quality = _QUALITY_AFTER_RESIZE
            logger.info("  Floor hit → shrinking to %dx%d | q=%d", new_w, new_h, quality)
        best_bytes = _encode_webp(current_img, quality)

    while len(best_bytes) < _TARGET_MIN and quality < _QUALITY_MAX:
        next_quality = min(_QUALITY_MAX, quality + _QUALITY_STEP)
        if next_quality == quality:
            break
        test_bytes = _encode_webp(current_img, next_quality)
        if len(test_bytes) < _TARGET_MAX:
            quality = next_quality
            best_bytes = test_bytes
            logger.info("  Small size detected → bumping quality to %d (size: %.2f KB)", quality, len(best_bytes)/1024)
        else:
            break

    final_kb   = len(best_bytes) / 1024
    reduction  = ((original_kb - final_kb) / original_kb * 100) if original_kb else 0
    final_w, final_h = current_img.size

    logger.info("Compression END | final=%.2f KB | reduction=%.1f%%", final_kb, reduction)

    metrics = {
        "original_size_kb": f"{round(float(original_kb), 2)} KB",
        "final_size_kb": f"{round(float(final_kb), 2)} KB",
        "reduction_percentage": f"{round(float(reduction), 1)}%",
        "final_quality": quality,
        "final_dimensions": f"{final_w}x{final_h}",
        "format": "WebP"
    }

    return best_bytes, metrics

def compress_video(raw_bytes: bytes, filename: str) -> tuple[bytes, dict]:
    """
    Compresses video using ffmpeg. Preserves the original format but tries to reduce size.
    Converting to mp4 (libx264) by default for compatibility.
    """
    original_size = len(raw_bytes)
    logger.info("Video Compression START | original=%.2f MB", original_size / (1024 * 1024))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as input_file:
        input_file.write(raw_bytes)
        input_name = input_file.name

    output_name = input_name + ".mp4"

    try:
        # ffmpeg -i input -vcodec libx264 -crf 28 -preset fast -y output
        command = [
            "ffmpeg", "-i", input_name, 
            "-vcodec", "libx264", "-crf", "28", 
            "-preset", "fast", 
            "-acodec", "aac", "-strict", "experimental",
            "-y", output_name
        ]
        
        logger.info("Executing video compression: %s", " ".join(command))
        process = subprocess.run(command, capture_output=True, text=True)
        
        if process.returncode != 0:
            logger.error("FFMPEG Error: %s", process.stderr)
            raise Exception("FFMPEG compression failed")

        with open(output_name, "rb") as f:
            best_bytes = f.read()

        final_size = len(best_bytes)
        reduction = ((original_size - final_size) / original_size * 100) if original_size else 0
        
        metrics = {
            "original_size": f"{round(float(original_size / (1024 * 1024)), 2)} MB",
            "final_size": f"{round(float(final_size / (1024 * 1024)), 2)} MB",
            "reduction": f"{round(float(reduction), 1)}%",
            "format": "mp4"
        }
        
        logger.info("Video Compression END | final=%.2f MB | reduction=%.1f%%", final_size / (1024 * 1024), reduction)
        return best_bytes, metrics

    finally:
        if os.path.exists(input_name):
            try: os.remove(input_name)
            except: pass
        if os.path.exists(output_name):
            try: os.remove(output_name)
            except: pass

def save_media(media_bytes: bytes, website_id: str, filename: str, ext: str) -> tuple[str, str]:
    folder    = Config.website_folder(website_id)
    fname     = f"{filename}.{ext}"
    full_path = os.path.join(folder, fname)

    with open(full_path, "wb") as fh:
        fh.write(media_bytes)

    relative_path = os.path.join(website_id, fname).replace("\\", "/")
    logger.info("Saved media → %s (%d bytes)", full_path, len(media_bytes))
    return relative_path, fname

def delete_image_file(relative_path: str) -> bool:
    full_path = os.path.join(Config.STORAGE_PATH, relative_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        logger.info("Deleted file → %s", full_path)
        return True
    logger.warning("File not found for deletion → %s", full_path)
    return False
