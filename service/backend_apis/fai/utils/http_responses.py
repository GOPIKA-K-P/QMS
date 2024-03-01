import json
from http import HTTPStatus
from typing import Any, Dict
from decimal import Decimal


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj)
        return json.JSONEncoder.default(self, obj)


def build_response(
    http_status: HTTPStatus,
    body: Dict[str, Any]
) -> Dict[str, Any]:
    data = json.dumps(body, cls=CustomEncoder) \
        if http_status >= 200 and http_status <= 204 else \
        json.dumps({"errors": body})
    return {
        'statusCode': http_status,
        'body': data,
        'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
        'isBase64Encoded': False,
        }


def response_json(
    http_status: int,
    data=None
) -> Dict[str, Any]:
    """
    making dict data
    Args:
        status (bool): status true/false
        data (list): actual data list or dict

    Returns:
        dict: json response
    """
    if data is None:
        data = {}
    return {"status": http_status, "data": data}
