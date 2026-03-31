import os
import logging
class Config:
    MAX_FILE_SIZE: int = 50 * 1024 * 1024          
    TARGET_MIN_BYTES: int = 15  * 1024             
    TARGET_MAX_BYTES: int = 295 * 1024             
    QUALITY_FLOOR: int = 45                        
    QUALITY_MAX:   int = 95                       
    
    ALLOWED_IMAGE_EXTENSIONS: set = {"jpg", "jpeg", "png", "webp", "gif"}
    ALLOWED_VIDEO_EXTENSIONS: set = {"mp4", "mov", "avi", "mkv", "webm"}
    ALLOWED_EXTENSIONS: set = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS

    ALLOWED_MIME_TYPES: set = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-matroska",
        "video/webm"
    }

    _BASE_DIR: str   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STORAGE_PATH: str = os.path.join(_BASE_DIR, "storage")
    LOG_DIR: str      = os.path.join(_BASE_DIR, "logs")

    # CORS Settings
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    MEDIA_BASE_URL: str   = os.getenv("MEDIA_BASE_URL", "http://localhost:8703")
    MEDIA_URL_PREFIX: str = "/media"

    LOG_FILE: str         = os.path.join(_BASE_DIR, "logs", "app.log")
    LOG_LEVEL: int        = logging.INFO
    LOG_MAX_BYTES: int    = 5 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 3
    LOG_FORMAT: str       = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    LOG_DATE_FORMAT: str  = "%Y-%m-%d %H:%M:%S"

    @classmethod
    def init_directories(cls) -> None:
        for directory in [cls.STORAGE_PATH, cls.LOG_DIR]:
            os.makedirs(directory, exist_ok=True)

    @classmethod
    def website_folder(cls, website_id: str) -> str:
        folder = os.path.join(cls.STORAGE_PATH, website_id)
        os.makedirs(folder, exist_ok=True)
        return folder

    @classmethod
    def media_url(cls, website_id: str, filename: str) -> str:
        return f"{cls.MEDIA_BASE_URL}{cls.MEDIA_URL_PREFIX}/{website_id}/{filename}"