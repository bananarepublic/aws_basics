import requests

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import define, options
from tornado.web import Application, RequestHandler
from tornado.httpclient import HTTPClient

define("port", default=8888, help="port to listen on")

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

def make_app():
    return Application([
        (r"/"    , MainHandler),
        (r"/info", InfoHandler),
    ])

def main():
    app = make_app()
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    print(f"Listening on http://0.0.0.0:{options.port}")
    IOLoop.current().start()

if __name__ == "__main__":
    main()
