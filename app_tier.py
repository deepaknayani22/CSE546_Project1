import base64

import boto3
from botocore.exceptions import ClientError
import logging
import os
import settings
import sqs_util
from subprocess import check_output
import json

# Constants
S3_INPUT_BUCKET = settings.S3_INPUT
S3_OUTPUT_BUCKET = settings.S3_OUTPUT
SQS_REQUEST_QUEUE_NAME = settings.SQS_INPUT
SQS_RESPONSE_QUEUE_NAME = settings.SQS_OUTPUT

# initialization and instantiations

sqs_management_instance = sqs_util

# app_sqs_resource = boto3.resource("sqs", region_name=constants.REGION_NAME)
app_sqs_client = boto3.client('sqs',
                              region_name=settings.REGION_NAME, aws_access_key_id=settings.KEY,
                              aws_secret_access_key=settings.KEY_PASS)

s3_client = boto3.client('s3',
                         region_name=settings.REGION_NAME, aws_access_key_id=settings.KEY,
                         aws_secret_access_key=settings.KEY_PASS)

response_queue_url = sqs_management_instance.get_queue_url(SQS_RESPONSE_QUEUE_NAME)
request_queue_url = sqs_management_instance.get_queue_url(SQS_REQUEST_QUEUE_NAME)


def get_message(queue_url):
    try:
        sqs_response = app_sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=20)
        message = sqs_response.get('Messages', None)
        if message:
            return message[0]
        else:
            return None
    except ClientError as e:
        logging.error(e)


def send_message_to_queue_response(queue_url, image_classification_key_value):
    try:
        response = app_sqs_client.send_message(QueueUrl=queue_url,
                                               MessageBody=image_classification_key_value)
        print("send_message_to_queue_response")
    except ClientError as e:
        logging.error(e)
        return False
    
def delete_message_request(queue_url, receipt_handle):
    try:
        app_sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle
                                      )
    except ClientError as e:
        logging.error(e)
        return False
    return True

def write_data_to_s3(file_name, bucket, data, debug=None):
    try:
        s3_client.upload_file(file_name, bucket, data)
        print(debug)
    except ClientError as e:
        logging.error(e)


# Write to a binary file
def write_to_file(image_name, result):
    with open(image_name, "wb") as f:
        f.write(bytes((result), 'utf8'))
        f.close()


def get_image_after_decoding_base64(msg_filename_key, msg_value):
    msg_value = bytes(msg_value, 'utf-8')
    with open('encode.bin', "wb") as file:
        file.write(msg_value)
    file = open('encode.bin', 'rb')
    byte = file.read()
    file.close()
    decodeit = open(msg_filename_key, 'wb')
    decodeit.write(base64.b64decode((byte)))
    decodeit.close()
    os.remove("encode.bin")

def classify_image_sub(base64ImageStr, imageName):
    base64Image = bytes(base64ImageStr, 'utf-8')
    with open(imageName, "wb") as fh:
        fh.write(base64.decodebytes(base64Image))
    out = check_output(["python3", "-W ignore", "../image_classification.py", imageName]).strip().decode('utf-8')
    return out

def get_file_contents(message):
    message_body = message.get("Body")
    response_json = json.loads(message_body)
    msg_filename_key = response_json.get('key')
    msg_base64_encoded_value = response_json.get('value')

    return (msg_filename_key, msg_base64_encoded_value)

if __name__ == '__main__':
    while True:
        print("running_app_tier start")
        message = get_message(sqs_management_instance.get_queue_url())
        if message is None:
            continue

        file_name, file_content = get_file_contents(message)
        
        classified_predicted_result = classify_image_sub(file_content, file_name)
        key_value_pair_predicted_json = json.dumps({'key': str(file_name), 'value': str(classified_predicted_result)})

        print("key_value_pair_predicted ")
        print(key_value_pair_predicted_json)

        write_data_to_s3(file_name, S3_INPUT_BUCKET, file_name, "Writing image to input S3")

        print("S3_OUTPUT_BUCKET :" + S3_OUTPUT_BUCKET + " Image File Name :" + file_name)
        print("Saved to s3 output bucket")
        # removing the Image png File
        send_message_to_queue_response(sqs_management_instance.get_queue_url(SQS_RESPONSE_QUEUE_NAME), key_value_pair_predicted_json)


        os.remove(file_name)
        file_name_without_jpg = str(file_name.split('.')[0])
        write_to_file(file_name_without_jpg, classified_predicted_result)
        write_data_to_s3(file_name_without_jpg, S3_OUTPUT_BUCKET, file_name_without_jpg, "Writing output to S3")
        
        # Deleting message after the message response is sent to queue
        delete_message_request(sqs_management_instance.get_queue_url(), message['ReceiptHandle'])
        os.remove(file_name_without_jpg)
