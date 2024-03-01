import json
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB client with region specified
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table_name = 'first_article_inspection'  # Replace with your DynamoDB table name
table = dynamodb.Table(table_name)

def get_items_from_dynamodb(tenant_id):
    response = table.query(
        KeyConditionExpression=Key('tenant_id').eq(tenant_id)
    )
    return response.get('Items', [])

def parse_inspection_date(inspection_date):
    if not inspection_date:
        return None, None
    parts = inspection_date.split("#")
    if len(parts) == 3:
        return parts[0], parts[1]
    return None, None

def lambda_handler(event, context):
    try:
        # Log the event for debugging purposes
        print("Received event:", json.dumps(event))
        
        # Ensure the event has the 'tenant_id' key
        tenant_id = event.get('tenant_id')
        if not tenant_id:
            return {
                "statusCode": 400,
                "body": {"error": "Key 'tenant_id' is missing in the request."}
            }

        # Retrieve items from DynamoDB based on 'tenant_id'
        items = get_items_from_dynamodb(tenant_id)

        # Check if any items were found
        if not items:
            return {
                "statusCode": 404,
                "body": {"error": f"No items found for tenant_id: {tenant_id}"}
            }

        # Prepare the response with the found items
        formatted_items = []
        for item in items:
            workorder_id, opn_no = parse_inspection_date(item.get("inspection_date"))
            formatted_item = {
                "tenant_id": item.get("tenant_id"),
                "part_id": item.get("part_id"),
                "fia_inspection_status": item.get("fia_inspection_status"),
                "inspection_date": item.get("inspection_date"),
                "workorder_id": workorder_id,
                "opn_no": opn_no
            }
            formatted_items.append(formatted_item)

        # Prepare the response with the found items
        return {
            "statusCode": 200,
            "body": {"items": formatted_items}
        }

    except Exception as e:
        # Handle exceptions
        error_message = f"Error retrieving items: {str(e)}"
        print("Error:", error_message)
        return {
            "statusCode": 500,
            "body": {"error": error_message}
        }
