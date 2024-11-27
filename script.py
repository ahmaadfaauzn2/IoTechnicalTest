import boto3
import json
import requests

# AWS S3 Configuration
AWS_ACCESS_KEY = ''
AWS_SECRET_KEY = ''
AWS_REGION = 'ap-southeast-1'
S3_BUCKET_NAME = 'wokwibuckets'
FILE_NAME = 'sensor_data.json'

# Kafka REST Proxy Configuration
REST_PROXY_URL = 'http://localhost:8082'  # Replace with your REST Proxy URL
CONSUMER_GROUP = 'sensor-group'
CONSUMER_INSTANCE = 'sensor-consumer'
TOPIC = 'sensor-data'

# Initialize S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def consume_kafka_data():
    """Create Kafka consumer, subscribe to topic, and fetch data."""
    try:
        # Step 1: Delete existing consumer instance (if any)
        delete_consumer_instance()

        # Step 2: Create Kafka Consumer
        create_consumer_url = f"{REST_PROXY_URL}/consumers/{CONSUMER_GROUP}"
        consumer_config = {
            "name": CONSUMER_INSTANCE,
            "format": "json",
            "auto.offset.reset": "earliest"
        }
        headers = {"Content-Type": "application/vnd.kafka.v2+json"}
        response = requests.post(create_consumer_url, headers=headers, json=consumer_config)

        if response.status_code != 200:
            print(f"Failed to create Kafka consumer: {response.status_code} {response.text}")
            return []

        # Step 3: Subscribe to the Topic
        subscription_url = f"{REST_PROXY_URL}/consumers/{CONSUMER_GROUP}/instances/{CONSUMER_INSTANCE}/subscription"
        subscription_config = {"topics": [TOPIC]}
        response = requests.post(subscription_url, headers=headers, json=subscription_config)

        if response.status_code != 204:
            print(f"Failed to subscribe to topic: {response.status_code} {response.text}")
            return []

        # Step 4: Fetch Records
        fetch_url = f"{REST_PROXY_URL}/consumers/{CONSUMER_GROUP}/instances/{CONSUMER_INSTANCE}/records"
        headers_fetch = {"Accept": "application/vnd.kafka.json.v2+json"}
        response = requests.get(fetch_url, headers=headers_fetch)

        if response.status_code != 200:
            print(f"Failed to fetch Kafka records: {response.status_code} {response.text}")
            return []

        return response.json()

    except Exception as e:
        print(f"Error consuming Kafka data: {e}")
        return []


def delete_consumer_instance():
    """Delete the existing Kafka consumer instance."""
    delete_url = f"{REST_PROXY_URL}/consumers/{CONSUMER_GROUP}/instances/{CONSUMER_INSTANCE}"
    try:
        response = requests.delete(delete_url)
        if response.status_code == 204:
            print(f"Successfully deleted existing consumer instance: {CONSUMER_INSTANCE}")
        else:
            print(f"Failed to delete consumer instance: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error deleting consumer instance: {e}")


def upload_to_s3(data):
    """Upload the data to AWS S3."""
    try:
        # Convert data to JSON string
        json_data = json.dumps(data)

        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=FILE_NAME,
            Body=json_data,
            ContentType='application/json'
        )
        print(f"Data uploaded successfully to S3 bucket '{S3_BUCKET_NAME}' as '{FILE_NAME}'.")
    except Exception as e:
        print(f"Failed to upload data to S3: {e}")

if __name__ == "__main__":
    print("Fetching data from Kafka...")
    kafka_data = consume_kafka_data()

    if kafka_data:
        print("Uploading data to S3...")
        upload_to_s3(kafka_data)
    else:
        print("No data to upload.")
