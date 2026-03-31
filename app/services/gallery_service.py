import logging
import os
import time
import urllib.request
import urllib.error
from app.config import Config
from app.validators.image_validator import MediaValidator
from app.utils.image_pipeline import compress_to_webp, compress_video, save_media, delete_image_file
logger = logging.getLogger(__name__)
_image_registry: dict[str, list[str]] = {}


def _download_url(url: str) -> tuple[bool, str, bytes]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "ImagePipeline/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_bytes = resp.read()
        logger.info("Downloaded URL '%s' → %d bytes", url, len(raw_bytes))
        return True, "", raw_bytes
    except urllib.error.URLError as exc:
        msg = f"Could not download URL: {exc.reason}"
        logger.warning(msg)
        return False, msg, b""
    except Exception as exc:
        msg = f"Unexpected error downloading URL: {exc}"
        logger.exception(msg)
        return False, msg, b""




class GalleryService:
    @staticmethod
    def upload_image(
        file,
        website_id: str,
        image_url: str = "",
        old_image_url: str = "",
    ) -> tuple[bool, str, dict, bool]:

        raw_bytes: bytes = b""
        dimensions: tuple[int, int] = (0, 0)
        media_type = "IMAGE"
        filename = ""

        if image_url:
            ok, err, raw_bytes = _download_url(image_url)
            if not ok:
                return False, err, {}, False

            class _BytesFile:
                filename = image_url.rsplit("/", 1)[-1] or "media.jpg"
                def read(self): return raw_bytes
                def seek(self, *a): pass

            valid, err_msg, raw_bytes, dimensions, media_type = MediaValidator.validate(_BytesFile())
            if not valid:
                return False, err_msg, {}, False
            filename = _BytesFile.filename

        elif file and getattr(file, "filename", ""):
            valid, err_msg, raw_bytes, dimensions, media_type = MediaValidator.validate(file)
            if not valid:
                return False, err_msg, {}, False
            filename = file.filename

        else:
            return False, "Provide either a file upload or a media URL", {}, False

        # registry logic
        if website_id not in _image_registry:
            folder = os.path.join(Config.STORAGE_PATH, website_id)
            if os.path.isdir(folder):
                disk_files = sorted(os.listdir(folder))
                _image_registry[website_id] = [f"{website_id}/{f}" for f in disk_files]
            else:
                _image_registry[website_id] = []

        existing_paths = _image_registry[website_id]
        is_replacement = False

        if old_image_url:
            media_marker = "/media/"
            if media_marker in old_image_url:
                rel_path = old_image_url.split(media_marker)[-1]
                if rel_path in existing_paths:
                    logger.info("Targeted replacement: deleting %s", rel_path)
                    delete_image_file(rel_path)
                    existing_paths.remove(rel_path)
                    is_replacement = True
                else:
                    logger.warning("old_media_url %s not found in registry for %s", rel_path, website_id)

        # compress based on type
        try:
            if media_type == "IMAGE":
                processed_bytes, metrics = compress_to_webp(raw_bytes, dimensions)
                ext = "webp"
            else:
                processed_bytes, metrics = compress_video(raw_bytes, filename)
                ext = "mp4" # We convert to mp4 in compress_video
        except Exception as exc:
            logger.exception("Media processing failed: %s", exc)
            return False, "Media processing failed", {}, False

        timestamp_ms = int(time.time() * 1000)
        stem         = f"{website_id}_{timestamp_ms}"

        try:
            relative_path, saved_filename = save_media(processed_bytes, website_id, stem, ext)
        except Exception as exc:
            logger.exception("Save failed: %s", exc)
            return False, "Could not store media", {}, False

    
        existing_paths.append(relative_path)
        _image_registry[website_id] = existing_paths
        
        public_url = Config.media_url(website_id, saved_filename)

        action = "REPLACED" if is_replacement else "ADDED"
        logger.info(
            "%s | website_id=%s | file=%s | size=%.2f KB | url=%s",
            action, website_id, saved_filename, len(processed_bytes) / 1024, public_url,
        )

        message = "Media replaced successfully" if is_replacement else "Media uploaded successfully"
        
        response_data = {
            "media_url": public_url,
            "media_type": media_type,
            "metrics": metrics
        }
        
        return True, message, response_data, is_replacement



    # GET 
    @staticmethod
    def get_image(website_id: str) -> tuple[bool, str, dict]:
        if website_id not in _image_registry:
            folder = os.path.join(Config.STORAGE_PATH, website_id)
            if os.path.isdir(folder):
                files = sorted(os.listdir(folder))
                _image_registry[website_id] = [f"{website_id}/{f}" for f in files]
            else:
                _image_registry[website_id] = []

        paths = _image_registry.get(website_id, [])

        if not paths:
            logger.warning("GET no media found for website_id=%s", website_id)
            return False, f"No media found for website '{website_id}'", {}

        media_urls = []
        valid_paths = []
        for p in paths:
            full_path = os.path.join(Config.STORAGE_PATH, p)
            if os.path.exists(full_path):
                filename = p.split("/")[-1]
                media_urls.append(Config.media_url(website_id, filename))
                valid_paths.append(p)
        
        _image_registry[website_id] = valid_paths

        if not media_urls:
            return False, "No valid media files found on disk", {}

        logger.info("GET OK | website_id=%s | count=%d", website_id, len(media_urls))

        return True, "Media fetched successfully", {
            "website_id": website_id,
            "media_urls": media_urls,
            "count": len(media_urls)
        }


    # DELETE 
    @staticmethod
    def delete_image(website_id: str, image_url: str = "") -> tuple[bool, str, dict]:
        if website_id not in _image_registry:
            folder = os.path.join(Config.STORAGE_PATH, website_id)
            if os.path.isdir(folder):
                disk_files = sorted(os.listdir(folder))
                _image_registry[website_id] = [f"{website_id}/{f}" for f in disk_files]
            else:
                _image_registry[website_id] = []

        paths = _image_registry.get(website_id, [])

        if not paths:
            logger.warning("DELETE no media found for website_id=%s", website_id)
            return False, f"No media found for website '{website_id}'", {}

        if image_url:
            media_marker = "/media/"
            rel_path = ""
            if media_marker in image_url:
                rel_path = image_url.split(media_marker)[-1]
            else:
                rel_path = f"{website_id}/{image_url.split('/')[-1]}"

            if rel_path in paths:
                if delete_image_file(rel_path):
                    paths.remove(rel_path)
                    _image_registry[website_id] = paths
                    
            
                    folder = os.path.join(Config.STORAGE_PATH, website_id)
                    if os.path.isdir(folder) and not os.listdir(folder):
                        os.rmdir(folder)
                        
                    return True, "Media deleted successfully", {"deleted_url": image_url}
                else:
                    return False, "Failed to delete media from disk", {}
            else:
                return False, f"Media '{rel_path}' not found in gallery for {website_id}", {}

        deleted_count = 0
        for rel_path in paths:
            if delete_image_file(rel_path):
                deleted_count += 1

        _image_registry.pop(website_id, None)

        folder = os.path.join(Config.STORAGE_PATH, website_id)
        if os.path.isdir(folder) and not os.listdir(folder):
            os.rmdir(folder)

        logger.info(
            "DELETE ALL OK | website_id=%s | deleted=%d files", website_id, deleted_count
        )
        return True, f"Deleted {deleted_count} media(s) for website '{website_id}'", {}
