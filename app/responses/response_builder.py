from datetime import datetime, timezone
from flask import jsonify


class ResponseBuilder:
    @staticmethod
    def _now_iso() -> str:
        return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")



    #SUCCESS
    @staticmethod
    def success(message: str, data: dict = None, status_code: int = 200):
        return jsonify({
            "status"        : True,
            "response_code" : status_code,
            "message"       : message,
            "data"          : data if data is not None else {},
        }), status_code

    @staticmethod
    def created(message: str, data: dict = None):
        return ResponseBuilder.success(message, data, status_code=201)

        

    #ERROR
    @staticmethod
    def error(message: str, data: dict = None, status_code: int = 400):
        return jsonify({
            "status"        : False,
            "response_code" : status_code,
            "message"       : message,
            "data"          : data if data is not None else {},
        }), status_code

    @staticmethod
    def bad_request(message: str, data: dict = None):
        return ResponseBuilder.error(message, data, status_code=400)

    @staticmethod
    def not_found(message: str = "Image not found", data: dict = None):
        return ResponseBuilder.error(message, data, status_code=404)

    @staticmethod
    def server_error(message: str = "Internal server error", data: dict = None):
        return ResponseBuilder.error(message, data, status_code=500)
