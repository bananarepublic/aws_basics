import os

import boto3

SNS_TOPIC = os.getenv('SNS_TOPIC')
SQS_QUEUE = os.getenv('SQS_QUEUE')


def send_sqs_messages_to_sns():
    sns = boto3.client('sns', region_name=get_region())
    sqs = boto3.client('sqs', region_name=get_region())

    while True:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE,
            WaitTimeSeconds=20,
        )

        if 'Messages' not in response:
            print('No messages')
            continue

        for message in response['Messages']:
            message_body = message['Body']
            response = sns.publish(
                TargetArn=SNS_TOPIC,
                Message=message_body,
                Subject='New Event',
            )
            print('Send message to SNS')
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(QueueUrl=SQS_QUEUE, ReceiptHandle=receipt_handle)
            print('Delete message from SQS')
