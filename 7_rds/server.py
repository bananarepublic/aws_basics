import os

import boto3
import requests

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, RequestHandler

define("port", default=8888, help="port to listen on")

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
S3_BUCKET = os.getenv('S3_BUCKET')



def instance_info():
    return requests.get(
        "http://169.254.169.254/latest/dynamic/instance-identity/document"
    ).json()


class MainHandler(RequestHandler):
    def get(self):
        self.write("Hello, world\n")


class InfoHandler(RequestHandler):
    def get(self):
        info = instance_info()
        region = info["region"]
        az = info["availabilityZone"]
        self.write(f"Region: {region}\n")
        self.write(f"AZ: {az}\n")


class FilesHandler(RequestHandler):
    def post(self, ignored):
        client = boto3.client("s3")
        print(self.request.files)
        for key in self.request.files:
            for file in self.request.files[key]:
                print(file)
                filename = file["filename"]
                body = file["body"]
                client.put_object(
                    Bucket=S3_BUCKET,
                    Key=filename,
                    Body=body,
                )
                self.set_status(201)
                self.write(f"{filename} {len(body)} bytes uploaded\n")

    def get(self, filename=None):
        client = boto3.client("s3")
        if filename:
            try:
                obj = client.get_object(
                    Bucket=S3_BUCKET,
                    Key=filename,
                )
                print(obj)
                self.set_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                self.write(obj["Body"].read())
            except client.exceptions.NoSuchKey:
                self.set_status(404)
                self.write(f"{filename} not found\n")
            except Exception as e:
                print(e)
                self.set_status(500)
        else:
            try:
                obj = client.list_objects(
                    Bucket=S3_BUCKET,
                )
                if "Contents" in obj:
                    contents = obj["Contents"]
                else:
                    contents = []

                print(contents)
                for c in contents:
                    filename = c["Key"]
                    size = c["Size"]
                    self.write(f"{filename} {size} bytes\n")

                self.write(f"{len(contents)} files\n")
            except Exception as e:
                print(e)
                self.set_status(500)

    def delete(self, filename):
        client = boto3.client("s3")
        try:
            obj = client.delete_object(
                Bucket=S3_BUCKET,
                Key=filename,
            )
            print(obj)
            self.write(f"{filename} deleted\n")
        except Exception as e:
            print(e)
            self.set_status(500)


def make_app():
    return Application([
        (r"/"    , MainHandler),
        (r"/info", InfoHandler),
        (r"/files/?([^/]+)?", FilesHandler),
    ], debug=True)


def main():
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print(f"Listening on http://0.0.0.0:{options.port}")
    IOLoop.current().start()


if __name__ == "__main__":
    main()
