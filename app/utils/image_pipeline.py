import logging
import os
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



_RESOLUTION_RULES: list[tuple[float, float, int]] = [
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
    
    
    #READ ORIGINAL SIZE
    original_size = len(raw_bytes)
    original_kb   = original_size / 1024
    width, height = dimensions
    logger.info("Compression START | original=%.2f KB | %dx%d", original_kb, width, height)
    img: Image.Image = Image.open(BytesIO(raw_bytes))
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGBA")
    elif img.mode != "RGB":
        img = img.convert("RGB")



    #RESOLUTION CONTROL
    mp = (width * height) / 1_000_000
    max_dim = _get_max_dimension(width, height)

    if max_dim is not None:
        logger.info("  Resolution Cap → %.2f MP → max_dim=%d px", mp, max_dim)
        img = _resize_to_max(img, max_dim)
    else:
        logger.info("  Resolution Cap → %.2f MP → keep original", mp)

    current_img = img




    #INITIal QUALITY
    quality = _get_initial_quality(original_size)
    logger.info("  Quality Map → initial quality=%d", quality)
    best_bytes = _encode_webp(current_img, quality)



    # GUARANTEE LOOP (DOWNWARD)
    while len(best_bytes) >= _TARGET_MAX:
        quality -= _QUALITY_STEP
        if quality < _QUALITY_FLOOR:
            w, h = current_img.size
            new_w, new_h = max(1, int(w * 0.90)), max(1, int(h * 0.90))
            current_img = current_img.resize((new_w, new_h), Image.LANCZOS)
            quality = _QUALITY_AFTER_RESIZE
            logger.info("  Floor hit → shrinking to %dx%d | q=%d", new_w, new_h, quality)

        best_bytes = _encode_webp(current_img, quality)

    # QUALITY RECOVERY
 
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



    #FINAL size
    final_kb   = len(best_bytes) / 1024
    reduction  = ((original_kb - final_kb) / original_kb * 100) if original_kb else 0
    final_w, final_h = current_img.size

    logger.info("Compression END | final=%.2f KB | reduction=%.1f%%", final_kb, reduction)

    metrics = {
        "original_size_kb": f"{round(original_kb, 2)} KB",
        "final_size_kb": f"{round(final_kb, 2)} KB",
        "reduction_percentage": f"{round(reduction, 1)}%",
        "final_quality": quality,
        "final_dimensions": f"{final_w}x{final_h}",
        "format": "WebP"
    }

    return best_bytes, metrics




# SAVE
def save_image(webp_bytes: bytes, website_id: str, filename: str) -> tuple[str, str]:
    folder    = Config.website_folder(website_id)
    fname     = f"{filename}.webp"
    full_path = os.path.join(folder, fname)

    with open(full_path, "wb") as fh:
        fh.write(webp_bytes)

    relative_path = os.path.join(website_id, fname).replace("\\", "/")
    logger.info("Saved image → %s (%d bytes)", full_path, len(webp_bytes))
    return relative_path, fname






#DELETE
def delete_image_file(relative_path: str) -> bool:
    full_path = os.path.join(Config.STORAGE_PATH, relative_path)
    if os.path.exists(full_path):
        os.remove(full_path)
        logger.info("Deleted file → %s", full_path)
        return True
    logger.warning("File not found for deletion → %s", full_path)
    return False
