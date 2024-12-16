# IoTechnicalTest (Ghosted xd)

# Part 1: Device Integration with Wokwi and Node-RED 
In this part, we integrate a simulated device on the Wokwi platform with Node-RED. The setup involves data transfer between the virtual microcontroller and Node-RED using MQTT, allowing real-time data logging and visualization.

- Objective
- Simulate a hardware environment using Wokwi.
- Establish communication between the Wokwi simulation and Node-RED.
- Log data into a CSV file.
- Display the data dynamically on a monitoring dashboard.

# Wiring Diagram 
![image](https://github.com/user-attachments/assets/d2aef32c-7673-4666-a78c-878e244a0f25)
![image](https://github.com/user-attachments/assets/996f6574-27f7-46bd-8cbb-f54fa20ef0c2)

# Code Snippets

```
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT credentials
const char* ssid = "Your_SSID";
const char* password = "Your_Password";
const char* mqtt_server = "Your_MQTT_Broker_Address";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setupWiFi();
  client.setServer(mqtt_server, 1883);
}

void setupWiFi() {
  delay(10);
  Serial.println("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("WiFi connected.");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Publish sensor data to Node-RED
  int sensorValue = analogRead(A0);
  client.publish("iot/sensor", String(sensorValue).c_str());

  delay(1000); // Publish every second
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("WokwiClient")) {
      Serial.println("Connected");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}
```

# Node Red Flow with json output and logging data.csv
Node-RED Flow Description
The flow:

- Receives MQTT messages from the Wokwi device.
- Parses and formats the data into JSON.
- Logs the data into a data.csv file.
- Outputs real-time data to the monitoring dashboard.
- 
Example Flow Code (JSON)
```
[
  {
    "id": "1",
    "type": "mqtt in",
    "z": "flow",
    "name": "MQTT Input",
    "topic": "iot/sensor",
    "qos": "2",
    "broker": "mqtt_broker_id",
    "x": 100,
    "y": 100,
    "wires": [["2"]]
  },
  {
    "id": "2",
    "type": "json",
    "z": "flow",
    "name": "",
    "property": "payload",
    "action": "obj",
    "x": 300,
    "y": 100,
    "wires": [["3", "4"]]
  },
  {
    "id": "3",
    "type": "file",
    "z": "flow",
    "name": "Log to CSV",
    "filename": "/data/data.csv",
    "appendNewline": true,
    "createDir": true,
    "overwriteFile": "false",
    "encoding": "none",
    "x": 500,
    "y": 100,
    "wires": []
  },
  {
    "id": "4",
    "type": "ui_chart",
    "z": "flow",
    "name": "Sensor Chart",
    "group": "ui_group_id",
    "order": 1,
    "width": "6",
    "height": "4",
    "x": 500,
    "y": 200,
    "wires": []
  }
]
```

![image](https://github.com/user-attachments/assets/92e1e92a-486a-46f8-befb-f464c6c56864)


# Monitoring Dashboard Integration
![image](https://github.com/user-attachments/assets/cb775bdd-81a8-48d2-8466-fecab60fdadf)


# Part 2 Data Streaming with Kafka

# Register confluent Platform 
Sign up for Confluent Cloud, a managed Apache Kafka service. This platform allows you to set up Kafka clusters in the cloud quickly.
![image](https://github.com/user-attachments/assets/09ba2c08-7bf3-4fbd-8922-fb8c089b0a19)

# Download and Extract Confluent Platform as Zip Files
Visit the Confluent Platform website and download the latest version as a ZIP file. Extract the ZIP file into a directory on your system.


# Create Kafka Topic in Confluent Cloud
- Navigate to the Confluent Cloud dashboard.
- Select your Kafka cluster.
- Create a new topic to store the streaming data.
![image](https://github.com/user-attachments/assets/44827eb2-773c-4398-ae0d-b263a46f3be5)

# Install WSL 
Install WSL on your system to run Linux-based commands and services. Follow the WSL installation guide to set it up.
![image](https://github.com/user-attachments/assets/3bcb1dee-dd62-4b06-afc4-7f3704103376)

# Install Java JDK 
Kafka requires Java to run. Install the Java Development Kit (JDK) to ensure compatibility with Kafka.
![image](https://github.com/user-attachments/assets/19132ea3-1db0-4ecf-8824-dcae4e5dd6b3)

# Create ccloud-kafka-rest.properties
```
bootstrap.servers=<YOUR_BOOTSTRAP_SERVER>
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="<API_KEY>" password="<API_SECRET>";
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
```

# Run Rest Proxy
```
./bin/kafka-rest-start /path/to/ccloud-kafka-rest.properties
```
![image](https://github.com/user-attachments/assets/db3e2ad4-cf35-45cc-bba9-d32f57a3aa5a)

# Integrate Node-RED with Kafka REST Proxy
a. Add HTTP Request and Function Nodes
- Open Node-RED.
- Install the http-request palette from the palette manager.
- Add the HTTP Request and Function nodes to your flow to interact with the Kafka REST Proxy.
![image](https://github.com/user-attachments/assets/6ba76dfe-4db6-4d12-9bf6-8a35d76072c2)

# Data Sended with POST method to the kafka rest proxy 
Use the HTTP Request node to send data to the Kafka REST Proxy. Configure the node to use the POST method, targeting the appropriate REST endpoint:
```
POST http://<REST_PROXY_HOST>:<REST_PROXY_PORT>/topics/<TOPIC_NAME>
```

The payload should be a JSON object representing the Kafka message:
```
{
  "records": [
    {
      "key": "sensor-1",
      "value": {
        "temperature": 22.5,
        "humidity": 60
      }
    }
  ]
}
```

![image](https://github.com/user-attachments/assets/16ece1e3-f4d1-4ab3-862f-a7701eecc52f)

# Confluent Cloud Topic message history
![image](https://github.com/user-attachments/assets/e08d7652-2c4d-4027-bfe3-c812a2ae258c)

## Steps to Achieve System Integration and Cloud Communication

# Part 3 System Integration and Cloud Communication
In this part, we integrate the IoT data pipeline with cloud services. The setup involves consuming Kafka topics, processing data, and storing it in AWS S3 using Python scripts and cloud monitoring tools like AWS CloudWatch.

# Register AWS S3 and choose Free Tier
Sign up for an AWS account and choose the Free Tier option to access AWS S3 for data storage. Create an S3 bucket to store the data streamed from Kafka.
![image](https://github.com/user-attachments/assets/fb4d1f2c-49e3-4b11-9653-cff76e86f1f6)


# Consume Kafka Topic from Confluent CLI
Use the Confluent CLI to consume messages from the Kafka topic you created earlier. This verifies that the data from Node-RED is successfully streaming into Kafka.
```
confluent kafka topic consume <TOPIC_NAME> --value-format json --from-beginning
```
![consumee](https://github.com/user-attachments/assets/b9ab8429-e4e4-48da-ac70-331e96ad0bc1)


# Install Dependency Kafka Python and boto3(aws s3)
Install the necessary Python libraries for integrating Kafka and AWS S3:

1. kafka-python: For consuming Kafka topics in Python.
2. boto3: For interacting with AWS S3.
   
Install Command:
```
pip install kafka-python boto3
```

![image](https://github.com/user-attachments/assets/e2318edd-748a-4033-9717-01642cdf70bb)


# Create Script to send kafka, change AWS S3 Config and Kafka Rest based on your own configuration!
Write a Python script to:

1. Consume data from the Kafka topic.
2. Process the JSON data.
Upload the processed data to AWS S3.
Key Components:
- Kafka Consumer: Connects to the Kafka broker and reads messages.
- AWS S3 Client: Uploads the messages to the designated S3 bucket.
Update the script with your AWS S3 bucket name, Kafka configuration, and REST Proxy settings.
Sample Code:
```
from kafka import KafkaConsumer
import boto3
import json

# Kafka and AWS configuration
KAFKA_BROKER = "<YOUR_KAFKA_BROKER>"
KAFKA_TOPIC = "<YOUR_TOPIC>"
AWS_S3_BUCKET = "<YOUR_BUCKET_NAME>"
AWS_REGION = "<YOUR_REGION>"

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize S3 client
s3 = boto3.client('s3', region_name=AWS_REGION)

# Process messages and upload to S3
for message in consumer:
    data = message.value
    file_name = f"data_{message.offset}.json"
    s3.put_object(Bucket=AWS_S3_BUCKET, Key=file_name, Body=json.dumps(data))
    print(f"Uploaded {file_name} to S3.")
```

![image](https://github.com/user-attachments/assets/21f41965-2639-486c-9d69-36f693e831ef)


# Run the script.py 
Execute the script to start consuming data from Kafka and uploading it to AWS S3.
```
python script.py
```
![image](https://github.com/user-attachments/assets/82e4eb61-f230-48cb-93ec-1e894e15f2fe)


# Data output from kafka and node -red in AWS Buckets
![image](https://github.com/user-attachments/assets/7a949b19-c003-4854-9e92-837f63ff6669)


# Json output from kafka
![image](https://github.com/user-attachments/assets/807558cb-7cb8-40c1-9443-840c33817608)


# Monitoring used Cloudwatch implemented 3 Services (PutBucketEncryption,GetBucketLoggin,GetBucketNotification)
Implement AWS CloudWatch to monitor the services used in this integration. Set up monitoring for the following AWS S3 operations:

PutBucketEncryption: Monitors encryption settings on your S3 bucket.
GetBucketLogging: Tracks access logs for the bucket.
GetBucketNotification: Ensures notification configurations are monitored.
CloudWatch Dashboard Example:
Include a screenshot of the CloudWatch dashboard for better visualization of the monitored metrics.
![image](https://github.com/user-attachments/assets/8874641d-9e02-4c0f-aad8-201936c568fa)


