def make_response(success=True, message="", data=None, notification_type="info", status_code=200):
    """
    Standardized API response helper with notification toast hints.
    notification_type: success, warning, error, info
    """
    return {
        "success": success,
        "message": message,
        "notification": {
            "type": notification_type,
            "message": message
        },
        "data": data or {}
    }, status_code
