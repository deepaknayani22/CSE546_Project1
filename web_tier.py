from quart import Quart, request, jsonify
from PIL import Image
import base64
import asyncio
import boto3
import json
import settings
import time
from sqs_util import *
from logging.config import dictConfig
#from threading import Thread
import threading

classification_output = {}

REQUEST_QUEUE_NAME = settings.SQS_INPUT
RESPONSE_QUEUE_NAME = settings.SQS_OUTPUT

app = Quart(__name__)
lock = threading.Lock()
def collect_response():
    while True:
        queue_url = get_queue_url(settings.SQS_OUTPUT)
        response = receive_message(queue_url)
        app.logger.debug("Recevied response from queue %s", response)
        for message in response:
            message_body = message['Body']
            message_dict = json.loads(message_body)
            
            lock.acquire()
            try:
                classification_output[message_dict['key']] = message_dict['value']
            finally:
                lock.release()
            delete_message(queue_url, message['ReceiptHandle'])
        #time.sleep(1)

async def get_result(key):
    while True:
        await asyncio.sleep(1)

        if key in classification_output:
            output_to_be_returned = '{0}'.format(classification_output[key])
            print("WebTier Output returned" + str(output_to_be_returned))
            del classification_output[key]
            return output_to_be_returned
        
        
@app.route('/classify-image', methods=['POST'])
async def classify_image():
    file = (await request.files)['myfile']
    file_content = file.read()
    value = base64.b64encode(file_content)
    value = str(value, 'utf-8')
    key = str(file.filename)
    json_msg = json.dumps({'key': key, 'value': value})
    
    queue_url = get_queue_url(settings.SQS_INPUT)
    send_message(queue_url, json_msg)

    # receive message from SQS
    return await get_result(key)
  

resultsThread = threading.Thread(target=collect_response)
resultsThread.start()
app.run(host='0.0.0.0', debug=True, port=6060)
