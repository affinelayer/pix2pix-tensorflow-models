"""
This is only useful for testing model serving locally with a different server.

Instead of using this, you should copy out the models and use server/serve.py in the pix2pix-tensorflow repo.
"""

import socket
import os
import argparse
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

allowed_origin = None
socket.setdefaulttimeout(30)


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
        self.send_header("Content-Type", "application/octet-stream")
        self.end_headers()
        with open(path, "rb") as f:
            self.wfile.write(f.read())


    def do_OPTIONS(self):
        self.send_response(200)
        if "origin" in self.headers:
            if allowed_origin is not None and self.headers["origin"] != allowed_origin:
                print("invalid origin %s" % self.headers["origin"])
                self.send_response(400)
                return
            self.send_header("access-control-allow-origin", self.headers["origin"])

        allow_headers = self.headers.get("access-control-request-headers", "*")
        self.send_header("access-control-allow-headers", allow_headers)
        self.send_header("access-control-allow-methods", "GET, OPTIONS")
        self.send_header("access-control-max-age", "3600")
        self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", help="allowed origin")
    parser.add_argument("--addr", default="", help="address to listen on")
    parser.add_argument("--port", default=6060, type=int, help="port to listen on")
    args = parser.parse_args()

    global allowed_origin
    allowed_origin = args.origin

    print('serving at http://%s:%d' % (args.addr, args.port))
    ThreadedHTTPServer((args.addr, args.port), Handler).serve_forever()


main()
