from datetime import datetime, timezone

from flask import request


def erro_response(error, message, status, details=None):
    return {
        "error": error,
        "message": message,
        "details": details or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": request.path
    }, status