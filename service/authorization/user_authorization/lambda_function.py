import requests
from http import HTTPStatus

from typing import Dict
from utils.observability import logger
from utils.check_permission import CheckApiPermissions


def lambda_handler(event: dict, context) -> Dict:
    '''
    To do User Authorization based on the JWT token
    Permission validation is happening through Request call
    '''
    try:
        # Initializing Output Response Body
        body = {
            "isAuthorized": False,
            "context": {}
        }

        # Get Headers
        logger.info(f"Events: {event}")
        authorization_header = event['headers']['authorization']
        logger.info(f"Authorization Header: {authorization_header}")
        tenant_id = event.get('headers', None).get('tenant_id', None)
        logger.info(f"Tenant ID: {tenant_id}, {tenant_id is None}")

        # Handling Payloads
        if tenant_id is None:
            logger.info(f"{body}, Tenant ID not present in Header")
            return body

        # Creating Headers for User Management API Call
        custom_headers = {
            "Content-Type": "application/json",
            "Authorization": authorization_header
        }
        api_path = event['requestContext']['http']['path']
        api_end_point = api_path.split("/")[-1]
        api_permissions = get_api_permissions(api_end_point)

        # Iterating list of API permissions and pass it to User management
        for permission in api_permissions:
            payload = {
                "permissionToCheck": permission
            }
            USER_AUTHORIZE_API = f"http://18.181.9.87:8081/v1/authorization/{tenant_id}/check_permission"
            response = requests.post(
                USER_AUTHORIZE_API, headers=custom_headers, json=payload)
            logger.info(response.json())

            if response.status_code == HTTPStatus.UNAUTHORIZED:
                logger.info(f"{body}, Token Expired")
                return body

            if response.status_code == HTTPStatus.OK:
                body["isAuthorized"] = True
                context_req = response.json().get("result", {})
                context_req["authorization_header"] = authorization_header
                body["context"] = context_req

        logger.info(f"Response body {body}")
        return body
    except requests.exceptions.ConnectionError as cre:
        logger.error(str(cre))
        msg = " [Errno 111] Connection refused"
        logger.info(f"Failed to establish a new connection:{msg}")
        return body
    except Exception as e:
        logger.error(str(e))
        return body


def get_api_permissions(api_end_point):
    '''
    To get the List of permissions defined for an API
    '''
    api_end_point = "/" + api_end_point
    check_api_permissions = CheckApiPermissions()
    return check_api_permissions.get_permissions(api_end_point)
