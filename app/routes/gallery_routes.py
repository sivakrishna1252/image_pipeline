import logging
from flask import Blueprint, request
from app.services.gallery_service import GalleryService
from app.responses.response_builder import ResponseBuilder
logger = logging.getLogger(__name__)
imagepipeline = Blueprint("imagepipeline", __name__)


# Health check
@imagepipeline.route("/", methods=["GET"])
def health_check():
    return "image pipeline is running-cms"



#PUT /gallery 
@imagepipeline.route("/gallery", methods=["PUT"], strict_slashes=False)
@imagepipeline.route("/gallery/<string:url_website_id>", methods=["PUT"], strict_slashes=False)
def put_image(url_website_id=None):
    file = request.files.get("file")
    json_body  = request.get_json(silent=True) or {}
    
    # Priority: URL path > Form data > JSON body
    website_id = (
        url_website_id 
        or request.form.get("website_id", "") 
        or json_body.get("website_id", "")
    ).strip()
    image_url = (
        request.form.get("image_url", "")
        or json_body.get("image_url", "")
        or json_body.get("file", "")         
    ).strip()
    old_image_url = (
        request.form.get("old_image_url", "")
        or json_body.get("old_image_url", "")
    ).strip()

    if not website_id:
        return ResponseBuilder.bad_request("'website_id' is required")

    has_file = file and file.filename
    has_url  = bool(image_url)

    if not has_file and not has_url:
        return ResponseBuilder.bad_request(
            "Provide either a file upload (multipart field 'file') "
            "or an image URL (JSON field 'image_url' or 'file')"
        )

    logger.info(
        "PUT /gallery | website_id=%s | source=%s | replace=%s",
        website_id,
        f"url={image_url}" if has_url else f"file={file.filename}",
        old_image_url if old_image_url else "none"
    )

    try:
        success, message, data, is_update = GalleryService.upload_image(
            file=file,
            website_id=website_id,
            image_url=image_url,
            old_image_url=old_image_url,
        )
    except Exception as exc:
        logger.exception("Unexpected error in PUT /gallery: %s", exc)
        return ResponseBuilder.server_error("Unexpected server error")

    if not success:
        return ResponseBuilder.bad_request(message)

    return ResponseBuilder.success(message, data)




#GET /gallery/<website_id>
@imagepipeline.route("/gallery/<string:website_id>", methods=["GET"], strict_slashes=False)
def get_image(website_id: str):
    logger.info("GET /gallery/%s", website_id)
    success, message, data = GalleryService.get_image(website_id)
    if not success:
        return ResponseBuilder.not_found(message)
    return ResponseBuilder.success(message, data)





#DELETE /gallery/<website_id>
@imagepipeline.route("/gallery/<string:website_id>", methods=["DELETE"], strict_slashes=False)
def delete_image(website_id: str):
    json_body = request.get_json(silent=True) or {}
    image_url = (request.form.get("image_url", "") or json_body.get("image_url", "")).strip()

    logger.info("DELETE /gallery/%s | target=%s", website_id, image_url if image_url else "ALL")
    
    success, message, data = GalleryService.delete_image(website_id, image_url)
    if not success:
        return ResponseBuilder.not_found(message)

    return ResponseBuilder.success(message, data)
