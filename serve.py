"""
This is only useful for testing model serving locally with a different server.

Instead of using this, you should copy out the models and use server/serve.py in the pix2pix-tensorflow repo.
"""

import os
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):

        filenames = [name for name in os.listdir(".") if not name.startswith(".")]
        path = self.path[1:]
        if path not in filenames:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"missing")
            return

        self.send_response(200)
        if "origin" in self.headers:
            self.send_header("access-control-allow-origin", self.headers["origin"])
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        with open(path, "rb") as f:
            self.wfile.write(f.read())


    def do_OPTIONS(self):
        self.send_response(200)
        if "origin" in self.headers:
            if a.origin is not None and self.headers["origin"] != a.origin:
                print("invalid origin %s" % self.headers["origin"])
                self.send_response(400)
                return
            self.send_header("access-control-allow-origin", self.headers["origin"])

        allow_headers = self.headers.get("access-control-request-headers", "*")
        self.send_header("access-control-allow-headers", allow_headers)
        self.send_header("access-control-allow-methods", "GET, OPTIONS")
        self.send_header("access-control-max-age", "3600")
        self.end_headers()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default=6060, type=int, help="port to listen on")
    args = parser.parse_args()

    server_address = ('', args.port)
    httpd = HTTPServer(server_address, Handler)
    print('serving at http://127.0.0.1:%d' % args.port)
    httpd.serve_forever()


main()
