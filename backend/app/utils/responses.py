from typing import Any

from fastapi import Response, status


def no_content() -> Response:
    """
    Standardized 204 response for empty bodies.
    """
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def message_response(message: str, code: int = status.HTTP_200_OK) -> dict[str, Any]:
    return {"message": message, "status": code}

