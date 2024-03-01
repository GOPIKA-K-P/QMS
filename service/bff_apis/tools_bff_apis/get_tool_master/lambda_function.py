import requests
from http import HTTPStatus
from dal import nosql_connection
from aws_lambda_powertools.utilities.typing import LambdaContext
from utils.http_responses import build_response
from utils.commonlib import geteway_api_url
from utils.observability import logger

table=nosql_connection('first_article_inspection')

def lambda_handler(event: dict, context: LambdaContext) -> dict:

    try:
        """
        This is to Get Tools master
        by communicating with Backend API
        instead of Database directly
        OUTPUT : Success Response
        """

        # Get Request Context to fetch token and decoded header values
        request_contexts = event.get(
            'requestContext', {}).get('authorizer', {}).get('lambda', {})
        logger.info(f"Request Context : {request_contexts}")

        # Get API Gateway Base URL
        api_end_point = geteway_api_url()
        if api_end_point is None:
            return build_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Issue while fetching API Base URL")

        # Creating headers if it is Auth BE API
        if request_contexts:
            auth_header = request_contexts.get("authorization_header")
        else:
            return build_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Issue while fetching Request Context")
        custom_headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        # Call BE API to get the Raw Data from DB
        get_fai_response = requests.get(
            api_end_point + "/v1.0/get_fai",
            headers=custom_headers)

        if get_fai_response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            return build_response(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                get_fai_response.json()
            )
        if get_fai_response.status_code == HTTPStatus.FORBIDDEN:
            return build_response(
                HTTPStatus.FORBIDDEN,
                get_fai_response.json()
            )

        # API Business Logic
        tenant_id=event['queryStringParameters']['tenant_id']
        fai_response=ytable.get_item(key='tenant_id')
        fai_item=fai_response.get('Item',{})

        return build_response(
            HTTPStatus.OK, get_fai_response.json({
                'fai': fai_item
            }))
    except requests.exceptions.ConnectionError as cre:
        logger.error(str(cre))
        msg = " [Errno 111] Connection refused"
        logger.error(f"Failed to establish a connection:{msg}")
        return build_response(
            HTTPStatus.INTERNAL_SERVER_ERROR, str(cre))
    except Exception as e:
        return build_response(
            HTTPStatus.INTERNAL_SERVER_ERROR, str(e))
