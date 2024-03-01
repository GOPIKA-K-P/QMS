from functools import wraps
from typing import Callable

from pydantic import ValidationError

from utils.http_responses import build_response


def query_validation_required(model):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(event, context):
            try:
                payload = {}
                if event.get('queryStringParameters', None):
                    payload = event.get('queryStringParameters')
                elif event.get('pathParameters', None):
                    payload = event.get('pathParameters')
                elif event.get('body', None):
                    payload = event.get('body')
                # Parse and validate the query parameters
                query_params = model(**payload)
                event["query_params"] = query_params
                return func(event, context)
            except ValidationError as e:
                error = [
                    {
                        "field_required": err.get("loc")[0]
                    } for err in e.errors()
                ]
                # Handle validation errors and return an error response
                return build_response(400, error)
        return wrapper
    return decorator


def response_json(status, data=None):

    """
    making json data
    Args:
        status (bool): status true/false
        data (list): actual data list or dict
    Returns:
        dict: json response
    """
    if data is None:
        data = {}
    return {"status": status, "data": data}
