import boto3
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


def geteway_api_url():
    base_url = None
    api_id = None
    api_end_point = None
    api_gateway_client = boto3.client("apigatewayv2")
    api_gateway_name = "pms-oee-backend-dev"
    gateway_info = api_gateway_client.get_apis()
    if gateway_info["Items"]:
        for items in gateway_info["Items"]:
            if items["Name"] == api_gateway_name:
                base_url = items["ApiEndpoint"]
                api_id = items["ApiId"]

    if api_id:
        gateway_stages = api_gateway_client.get_stages(ApiId=api_id)
        stage_name = gateway_stages["Items"][0]["StageName"]
        api_end_point = base_url + "/" + stage_name

    return api_end_point
