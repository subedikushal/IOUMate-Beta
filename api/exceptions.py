from rest_framework.views import exception_handler
from .utils import message


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    try:
        if response is not None and response.data['password'].code == 'invalid':
            response.data = message("Password didn't matched.", False)
            return response
        if response is not None and response.data['detail'].code == 'not_authenticated':
            response.data = message("User not authenticated.", False)
            return response
    except Exception:
        return response
