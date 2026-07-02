from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ResponseHandler:

    @staticmethod
    def response(message, data=None, errors=None, status_code=status.HTTP_200_OK):
        is_success = 200 <= status_code < 300
        body = {
            "status": is_success,
            "message": message,
        }
        if data is not None:
            body["data"] = jsonable_encoder(data)
        if errors is not None:
            body["errors"] = errors
        return JSONResponse(content=body, status_code=status_code)

    @staticmethod
    def ok(message="Success", data=None):
        return ResponseHandler.response(message, data, status_code=status.HTTP_200_OK)

    @staticmethod
    def created(message="Created successfully", data=None):
        return ResponseHandler.response(message, data, status_code=status.HTTP_201_CREATED)

    @staticmethod
    def bad_request(message="Bad request", errors=None):
        return ResponseHandler.response(message, errors=errors, status_code=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def unprocessable_entity(message="Unprocessable entity", errors=None):
        return ResponseHandler.response(message, errors=errors, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @staticmethod
    def unauthorized(message="Unauthorized"):
        return ResponseHandler.response(message, status_code=status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def forbidden(message="Forbidden"):
        return ResponseHandler.response(message, status_code=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def not_found(message="Not found"):
        return ResponseHandler.response(message, status_code=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def server_error(message="Internal server error"):
        return ResponseHandler.response(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def too_many_requests(message="Too many requests", data=None):
        return ResponseHandler.response(message, data, status_code=status.HTTP_429_TOO_MANY_REQUESTS)
