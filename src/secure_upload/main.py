#!/usr/bin/env python3
import argparse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler, test
from typing import Any
# local files
from .server import CustomRequestHandler

def parse_args() -> Any:
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--http-port", nargs="?", type=int, default=8000, help="the port to bind the HTTP server to. Defaults to 8000")
    ap.add_argument("-b", "--bind", default=None, metavar="ADDRESS",
        help="Specify alternate bind address. Defaults to all interfaces")
    return ap.parse_args()

def main():
    args = parse_args()

    test(
        HandlerClass=CustomRequestHandler,
        ServerClass=ThreadingHTTPServer,
        port=args.http_port,
        bind=args.bind,
    )


if __name__ == "__main__":
    main()
