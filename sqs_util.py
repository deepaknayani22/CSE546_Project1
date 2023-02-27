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


def delete_message(QueueUrl, receipt_handle):
    response = client.delete_message(
        QueueUrl=QueueUrl,
        ReceiptHandle=receipt_handle,
    )
    print(response)
