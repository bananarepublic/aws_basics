import os
import threading

import boto3
import requests

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, RequestHandler

HTTP_PORT = 8888
define('port', default=HTTP_PORT, help='port to listen on')

S3_BUCKET = os.getenv('S3_BUCKET')
SNS_TOPIC = os.getenv('SNS_TOPIC')
SQS_QUEUE = os.getenv('SQS_QUEUE')


def instance_info():
    return requests.get(
        'http://169.254.169.254/latest/dynamic/instance-identity/document'
    ).json()


def get_public_ip():
    return requests.get('http://169.254.169.254/latest/meta-data/public-ipv4').text


def get_region():
    ec2_info = instance_info()
    region = ec2_info['region']
    return region


def get_az():
    ec2_info = instance_info()
    az = ec2_info['availabilityZone']
    return az


class MainHandler(RequestHandler):
    def get(self):
        self.write('Hello, world\n')


class InfoHandler(RequestHandler):
    def get(self):
        region = get_region()
        az = get_az()
        self.write(f'Region: {region}\n')
        self.write(f'AZ: {az}\n')


class FilesHandler(RequestHandler):
    def post(self, ignored):
        s3 = boto3.client('s3')
        sqs = boto3.client('sqs', region_name=get_region())
        print(self.request.files)
        for key in self.request.files:
            for file in self.request.files[key]:
                print(file)
                filename = file['filename']
                body = file['body']
                s3.put_object(
                    Bucket=S3_BUCKET,
                    Key=filename,
                    Body=body,
                )

                event_type = 'file_uploaded'
                file_size = len(body)
                file_name, file_ext = os.path.splitext(filename)
                file_url = f'http://{get_public_ip()}:{HTTP_PORT}/files/{filename}'
                message_body = (
                    f'Event Type: {event_type}\n'
                    f'File Name: {file_name}\n'
                    f'File Ext: {file_ext}\n'
                    f'File Size: {file_size}\n'
                    f'File URL: {file_url}\n'
                )
                sqs.send_message(
                    QueueUrl=SQS_QUEUE,
                    MessageBody=message_body,
                )
                print('Send message to SQS')

                self.set_status(201)
                self.write(f'{filename} {len(body)} bytes uploaded\n')

    def get(self, filename=None):
        s3 = boto3.client('s3')
        if filename:
            try:
                obj = s3.get_object(
                    Bucket=S3_BUCKET,
                    Key=filename,
                )
                print(obj)
                self.set_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.write(obj['Body'].read())
            except s3.exceptions.NoSuchKey:
                self.set_status(404)
                self.write(f'{filename} not found\n')
            except Exception as e:
                print(e)
                self.set_status(500)
        else:
            try:
                obj = s3.list_objects(
                    Bucket=S3_BUCKET,
                )
                if 'Contents' in obj:
                    contents = obj['Contents']
                else:
                    contents = []

                print(contents)
                for c in contents:
                    filename = c['Key']
                    size = c['Size']
                    self.write(f'{filename} {size} bytes\n')

                self.write(f'{len(contents)} files\n')
            except Exception as e:
                print(e)
                self.set_status(500)

    def delete(self, filename):
        s3 = boto3.client('s3')
        try:
            obj = s3.delete_object(
                Bucket=S3_BUCKET,
                Key=filename,
            )
            print(obj)
            self.write(f'{filename} deleted\n')
        except Exception as e:
            print(e)
            self.set_status(500)


class SubsHandler(RequestHandler):
    def post(self, email=None):
        """Create email subscription."""
        sns = boto3.client('sns', region_name=get_region())
        if email:
            try:
                response = sns.subscribe(
                    TopicArn=SNS_TOPIC,
                    Protocol='email',
                    Endpoint=email,
                )

                self.write('Please visit your email to confirm subscription\n')
            except Exception as e:
                print(e)
                self.set_status(500)
        else:
            self.set_status(404)

    def get(self, ignored):
        """List all email subscriptions."""
        sns = boto3.client('sns', region_name=get_region())
        try:
            response = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC)
            subs = [sub['Endpoint'] for sub in response['Subscriptions']]

            for sub in subs:
                self.write(f'{sub}\n')

            self.write(f'{len(subs)} subscriptions\n')
        except Exception as e:
            print(e)
            self.set_status(500)

    def delete(self, email):
        """Delete email subscription."""
        sns = boto3.client('sns', region_name=get_region())
        try:
            response = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC)
            subs = response['Subscriptions']

            for sub in subs:
                if sub['Protocol'] == 'email' and sub['Endpoint'] == email:
                    sns.unsubscribe(SubscriptionArn=sub['SubscriptionArn'])
                    break

            self.write(f'{email} unsubscribed\n')
        except Exception as e:
            print(e)
            self.set_status(500)


def make_app():
    return Application([
        (r'/', MainHandler),
        (r'/info', InfoHandler),
        (r'/files/?([^/]+)?', FilesHandler),
        (r'/subs/?([^/]+)?', SubsHandler),
    ], debug=True)


def main():
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print(f'Listening on http://0.0.0.0:{options.port}')
    IOLoop.current().start()


if __name__ == '__main__':
    main()
