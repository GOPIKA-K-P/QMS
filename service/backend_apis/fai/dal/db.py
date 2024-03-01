import logging
from dal import nosql_connection
from utils.http_responses import response_json


class NoSqlBuilder:
    """
    This Package will help to handle NosqlDBs
    for currently should support Dynamodb(CRUD)
    """

    def __init__(self, table):
        self.table = nosql_connection.Table(table)

    def get(
            self,
            query_param,
            projection=None,
            limit=0,
            last_evaluated_key=None
        ):
        """
        NosqlDB get method
        call method ex: obj.get({})
        Args:
            query_param (dict): {"id": 2}
            projection: "col1, col2, col3"
        Returns:
            dict: {"status": True/False, "data": {"records": [], "count": 0}}
        """
        try:
            filter_expression = ' AND '.join(
                [
                    f'{key} = :{key}'
                    for key, value in query_param.items() if value
                ]
            )
            expression_attribute_values = {
                f':{key}': value for key, value in query_param.items()
                if value}

            condition = {}
            if query_param:
                condition["FilterExpression"] = filter_expression
                condition["ExpressionAttributeValues"] = \
                    expression_attribute_values

            if limit:
                condition["Limit"] = limit
            if projection:
                condition["ProjectionExpression"] = ", ".join(projection)
            if last_evaluated_key:
                condition["ExclusiveStartKey"] = last_evaluated_key

            if condition:
                result = self.table.scan(**condition)
            else:
                result = self.table.scan()

            return self._extracted_response_validation(result)
        except (nosql_connection.meta.client.exceptions.ClientError) as e:
            return response_json(False, str(e))

    def search(
        self,
        pk_query,
        query=None,
        projection=None,
        limit=0,
        order_by="ASC"
    ):
        try:
            condition = {}
            key_condition = ' AND '.join(
                    [
                        f'{key} = :{key}'
                        for key, value in pk_query.items() if value
                    ]
                )
            expr_attr_value = {
                    f':{key}': value for key, value in pk_query.items()
                    if value
                    }

            if query:
                filter_expression = ' AND '.join(
                    [
                        f'{key} = :{key}'
                        for key, value in query.items() if value
                    ]
                )
                condition['FilterExpression'] = filter_expression
                expr_attr = {
                    f':{key}': value for key, value in query.items()
                    if value
                    }
                expr_attr_value |= expr_attr

            if limit:
                condition["Limit"] = limit
            condition["KeyConditionExpression"] = key_condition
            condition["ExpressionAttributeValues"] = expr_attr_value
            if projection:
                condition["ProjectionExpression"] = ", ".join(projection)
            if order_by:
                condition["ScanIndexForward"] = order_by == "ASC"
            result = self.table.query(**condition)

            return self._extracted_response_validation(result)
        except (nosql_connection.meta.client.exceptions.ClientError) as e:
            return response_json(False, str(e))

    # this here and in `get` and `search`
    def _extracted_response_validation(self, result):
        if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return response_json(False, result["Error"]["Message"])
        result = {
            "records": result['Items'],
            "count": result['Count'],
            "last_evaluated_key": result.get("LastEvaluatedKey", {})
        }
        return response_json(True, result)

    def add(self, payload):
        """
        NosqlDB add method
        call method ex: obj.add({})
        Args:
            payload (dict): {"order_id": "", "order_name": ""}

        Returns:
            dict: {"status": True/False, "data": {}}
        """
        try:
            if isinstance(payload, list):
                with self.table.batch_writer() as batch:
                    for item in payload:
                        result = batch.put_item(Item=item)
            if isinstance(payload, dict):
                result = self.table.put_item(Item=payload)
                if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
                    return response_json(False, result["Error"]["Message"])
            return response_json(True)
        except (nosql_connection.meta.client.exceptions.ClientError) as e:
            return response_json(False, str(e))

    def update(self, query, payload):
        """
        NosqlDB update method
        call method ex: obj.update({})
        Args:
            payload (dict): {"order_name": "updated_value"}

        Returns:
            dict: {"status": True/False, "data": {}}
        """
        try:
            update_expr = [f'{col} = :{col}' for col in payload.keys()]
            attr_val = {f':{col}': val for col, val in payload.items()}

            update_expression = 'SET ' + ', '.join(update_expr)
            expression_attribute_values = attr_val

            logging.info(query, update_expression, expression_attribute_values)
            result = self.table.update_item(
                Key=query,
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return response_json(False, result["Error"]["Message"])
            return response_json(True)
        except (nosql_connection.meta.client.exceptions.ClientError) as e:
            return response_json(False, str(e))

    def delete(self, query):
        """
        NosqlDB delete method
        call method ex: obj.delete({})
        Args:
            payload (dict): {"id": 2}

        Returns:
            dict: {"status": True/False, "data": {}}
        """
        try:
            result = self.table.delete_item(Key=query)
            if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
                return response_json(False, result["Error"]["Message"])
            return response_json(True)
        except (nosql_connection.meta.client.exceptions.ClientError) as e:
            response_json(False, str(e))
