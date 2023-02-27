from asyncio import constants
import boto3
import logging
import settings
import json
import os
from botocore.exceptions import ClientError

REQUEST_QUEUE_NAME = settings.SQS_INPUT
RESPONSE_QUEUE_NAME = settings.SQS_OUTPUT

client = boto3.client('sqs', region_name=settings.REGION_NAME,  aws_access_key_id=settings.KEY,
                                                                 aws_secret_access_key=settings.KEY_PASS)

# def create_SQS_queue(SQS_QUEUE_NAME=REQUEST_QUEUE_NAME):
#     try:
#         queue = client.create_queue(
#             QueueName=SQS_QUEUE_NAME,
#             Attributes={
#                 'DelaySeconds': '15',
#                 'MaximumMessageSize': '262144',
#                 'VisibilityTimeout': '60',
#                 'MessageRetentionPeriod': '86400'
#             }
#         )
#         return queue['QueueUrl']
#     except:
#         logging.error(
#             "Unable to create a SQS queue with the given name, recheck the queue name")

def get_queue_url(queue_name=REQUEST_QUEUE_NAME):
    return client.get_queue_url(QueueName=queue_name)['QueueUrl']

def send_message(queueUrl, msg):
    response = client.send_message(
        QueueUrl=queueUrl,
        MessageBody=msg
    )
    logging.debug(response.get('MessageId'))


def receive_message(queueUrl):
    response = client.receive_message(
        QueueUrl=queueUrl,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )
    return response.get('Messages', [])
    # print(f"Number of messages received: {len(response.get('Messages', []))}")
    # for message in response.get("Messages", []):
    #     message_body = message["Body"]
    #     print(f"Message body: {json.loads(message_body)}")
    #     print(f"Receipt Handle: {message['ReceiptHandle']}")


def delete_message(QueueUrl, receipt_handle):
    response = client.delete_message(
        QueueUrl=QueueUrl,
        ReceiptHandle=receipt_handle,
    )
    print(response)

# def numberOfMessagesInQueue(queue_name=REQUEST_QUEUE_NAME):
#     response = client.get_queue_attributes(
#         QueueUrl=get_queue_url(queue_name),
#         AttributeNames=['ApproximateNumberOfMessages']
#     )
#     number = -1
#     if response['Attributes'] and response['Attributes']['ApproximateNumberOfMessages']:
#         number = response['Attributes']['ApproximateNumberOfMessages']
#     logging.debug("numberOfMessagesInQueue %s %s", queue_name, int(number))
#     return int(number)
