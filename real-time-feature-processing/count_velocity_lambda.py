import boto3
import base64
import json
from datetime import datetime, timedelta, timezone

# Setup
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("A2PAggregates")
window_minutes = 10

def lambda_handler(event, context):
    now = datetime.now(timezone.utc)
    
    for record in event["Records"]:
        # Decode and parse Kinesis record
        payload = base64.b64decode(record["kinesis"]["data"]).decode("utf-8")
        data = json.loads(payload)
        
        phone_range = data["phone_range"]
        score = data["score"]
        channel = data["channel"]  # e.g. 'a2p'
        
        # Create partition and sort key
        pk = f"{phone_range}_score_{score}_{channel}"
        sk = now.strftime("%Y-%m-%dT%H:%M")

        # --- Step 1: Update count atomically in current time bucket ---
        table.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression="ADD #c :inc",
            ExpressionAttributeNames={"#c": "count"},
            ExpressionAttributeValues={":inc": 1}
        )

        # --- Step 2: Query last N buckets to compute velocity ---
        keys = [
            {"pk": pk, "sk": (now - timedelta(minutes=i)).strftime("%Y-%m-%dT%H:%M")}
            for i in range(window_minutes)
        ]

        # Use batch_get_item (max 100 items)
        client = boto3.client("dynamodb")
        response = client.batch_get_item(
            RequestItems={
                table.name: {
                    "Keys": [{"pk": {"S": k["pk"]}, "sk": {"S": k["sk"]}} for k in keys]
                }
            }
        )

        total = sum(
            int(item["count"]["N"])
            for item in response["Responses"].get(table.name, [])
        )

        velocity = total / window_minutes

        # --- Optional: Emit velocity or take action ---
        print(f"[{pk}] Velocity = {velocity:.2f} events/min")

        # Optionally: trigger alert, publish to another stream, write to S3, etc.

    return {"status": "ok"}