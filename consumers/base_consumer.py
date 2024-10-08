from utils import TOPIC_CONFIG, TOPIC_TO_KEY
import json
import io,os
import time
from collections import defaultdict
import s3fs
from minio.error import S3Error
import minio
import avro.schema
from avro.io import DatumReader
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

# Kafka broker address
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9093']

class BaseKafkaConsumer:
    """
    BaseKafkaConsumer is a generic Kafka consumer class designed to consume messages from a specific topic, 
    deserialize the Avro-encoded messages, batch them by user, and upload these batches to MinIO storage.
    """

    # Class-level constants for batch size and time interval for batch processing
    BATCH_SIZE = 1  # Number of messages to batch before uploading to storage
    MAX_BATCH_TIME = 100  # Maximum time to wait before forcing a batch upload
    CONTAINER = "raw" # Cannot capitalize bucket names in Minio

    def __init__(self, topic):
        """
        Initializes the Kafka consumer with a specific topic and consumer group ID.

        Args:
            topic (str): The Kafka topic to subscribe to.
            consumer_group_id (str): The consumer group ID for managing Kafka offsets.
        """
        self.topic = topic  # Topic to subscribe to
        self.user_batches = defaultdict(list)  # Store batches of messages by user
        self.active_users = set()  # Track active users to manage batches

    def avro_deserializer(self, avro_bytes, schema):
        """
        Deserializes Avro-encoded messages.

        Args:
            avro_bytes (bytes): The Avro-encoded message.
            schema (avro.schema.Schema): The Avro schema for decoding.

        Returns:
            dict: The deserialized message as a Python dictionary.
        """
        try:
            reader = DatumReader(schema)  # Create an Avro DatumReader for schema
            bytes_reader = io.BytesIO(avro_bytes)  # Read bytes into a BytesIO buffer
            decoder = avro.io.BinaryDecoder(bytes_reader)  # Create a BinaryDecoder from the buffer
            return reader.read(decoder)  # Deserialize and return the message
        except Exception as e :
            print(f"schema mismatch:  {e}")

    def ensure_bucket_exists(self, client, bucket_name):
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        else:
            print(f"Bucket '{bucket_name}' already exists")


    def minio(self, user, topic, data, offset):
        """
        Uploads batched data to MinIO (an S3-compatible object storage).

        Args:
            user (str): The user associated with the data batch.
            topic (str): The Kafka topic name.
            data (list): The batch of messages to upload.
            offset (int): The offset of the last message in the batch.
        """
        topic = topic.replace("_", "-")
        try:

            # Set up S3 filesystem (MinIO uses S3 protocol)
            fs = s3fs.S3FileSystem(
                endpoint_url=f"http://localhost:9000",  # MinIO endpoint
                key="minioadmin",  # Access key
                secret="minioadmin"  # Secret key
            )

            # Convert data to JSON format
            obj = json.dumps(data)

            # Check if the bucket exists, create it if it doesn't
            if not fs.exists(BaseKafkaConsumer.CONTAINER):
                print("In container section\n")
                fs.mkdir(BaseKafkaConsumer.CONTAINER)
                print(f"Bucket '{BaseKafkaConsumer.CONTAINER}' created.")

            # Check if the topic subfolder exists, create it if it doesn't
            topic_path = f"{BaseKafkaConsumer.CONTAINER}/{topic}"
            if not fs.exists(topic_path):
                print("In topic section")
                fs.mkdir(topic_path)
                print(f"Topic folder '{topic}' created.")

            # Check if the user subfolder exists, create it if it doesn't
            user_path = f"{topic_path}/{user}"
            if not fs.exists(user_path):
                fs.mkdir(user_path)
                print(f"Subfolder '{user}' created in bucket '{topic}'.")

            # Write the data to MinIO
            with fs.open(f"{user_path}/{offset}.json", 'w') as f:
                f.write(obj)

            print(f"{offset} is successfully uploaded as object {topic}/{offset} to bucket {user}")
        except S3Error as e:
            print(f"Error occurred: {e}")
        except Exception as e:
            print(f"Error in MinIO function: {e}")

    def upload_user_batch(self, user, offset):
        """
        Uploads a batch of messages for a specific user to MinIO storage and clears the batch.

        Args:
            user (str): The user whose batch is being uploaded.
            offset (int): The offset of the last message in the batch.
        """
        self.minio(user, self.topic, self.user_batches[user], offset)  # Upload the batch to MinIO
        self.user_batches[user] = []  # Clear the batch after uploading

    def process_message(self, message):
        """
        Processes a Kafka message by deserializing it, batching it by user, and uploading the batch if the size threshold is reached.

        Args:
            message (dict): The Kafka messages polled from the consumer.
        """
        # Get the list of ConsumerRecords from the Kafka message for the subscribed topic partition
        records = list(message.values())[0]  # Extract multiple records
        # print(f"records: {records}\n")
        # Iterate over each ConsumerRecord in the list
        for record in records:
            # print(f"record: {record}")
            # Extract topic key, user identifier, and offset from the record
            topic_key, user, offset = TOPIC_TO_KEY[record.topic], record.key.decode("utf-8"), record.offset

            # Deserialize the Avro-encoded message
            data = self.avro_deserializer(record.value, TOPIC_CONFIG[topic_key]['schema'])

            # Append the deserialized data to the user's batch
            self.user_batches[user].append(data)

            # Check if the batch size has reached the threshold
            if len(self.user_batches[user]) >= BaseKafkaConsumer.BATCH_SIZE:
                print(f"Upload data to {self.topic}/{user}")
                # Upload the batch and reset
                self.upload_user_batch(user, offset)

    def consume(self, consumer):
        """
        Continuously consumes messages from the Kafka topic, processes them, and commits offsets after processing.
        """
        try:
            while True:
                print("Polling for messages")
                # Poll for messages with a timeout of 3000ms (3 seconds)
                message = consumer.poll(timeout_ms=3000)
                
                if message:
                    print(f"Received message")
                    # Process the received message batch
                    self.process_message(message)
                    # Commit the offset after processing messages
                    consumer.commit()
                else:
                    print("No messages received.")

        except KeyboardInterrupt as e:
            print(f"Stopping consumer for topic: {self.topic}")
        finally:
            # Close the consumer gracefully
            consumer.close()
