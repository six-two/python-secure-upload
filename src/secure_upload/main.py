#!/usr/bin/env python3
import argparse
import functools
from http.server import ThreadingHTTPServer, test
from typing import Any

from secure_upload.upload.gpg import GpgUploadHandler
from secure_upload.upload.handler import ModuleHandler
# local files
from .server import CustomRequestHandler
from .client_auth import HttpBasicAuthClientAuthenticator, MultiClientAuthenticator
from .ip_blocking import IpAddressBlocker

def parse_args() -> Any:
    default_block_threshold = 2
    default_block_duration = 15
    # Maximum auth guesser per IP address per second: default_block_threshold / default_block_duration
    # This is currently 2/15 = 0.1333_

    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--http-port", nargs="?", type=int, default=8000, help="the port to bind the HTTP server to. Defaults to 8000")
    ap.add_argument("-b", "--bind", default=None, metavar="ADDRESS",
        help="Specify alternate bind address. Defaults to all interfaces (and both IPv4 and IPv6, which may render IP address based blocking nearly useless)")

    auth_group = ap.add_argument_group("Authentication", "Authentication is used to prevent random people from interacting with the web server. You will need to enable at least one of the following options. Since authentication credentials may be passed on plain text or weakly hashed form, DO NOT REUSE THESE CREDENTIALS FOR ANYTHING ELSE (especially not as encryption password)!")
    auth_group.add_argument("--http-basic", metavar=("USERNAME", "PASSWORD"), nargs=2, required=False, help="HTTP Basic authentication. Widely supported, but transmits credentials in plain text")

    ip_group = ap.add_argument_group("IP based access control", "IP based access control aims to prevent unauthorized access and limit brute force attacks against the authentication.")
    ip_group.add_argument("--allow-ips", nargs="*", default=[], help="always allow access from these IP addresses (even when they repeatedly fail authentication)")
    ip_group.add_argument("--deny-ips", nargs="*", default=[], help="never allow connections from these IP addresses. If both --allow-ips and --deny-ips contain the same address, --deny-ips will take priority")
    ip_group.add_argument("--block-threshold", nargs="?", type=int, default=default_block_threshold, help=f"after how many failed authentication attempts an IP address is temporarily blocked. Defaults to {default_block_threshold}")
    ip_group.add_argument("--block-duration", nargs="?", type=int, default=default_block_duration, help=f"BLOCK_DURATION seconds after the first failed login, all blocks and failed login counters will be reset. So consider this the maximum block duration. Defaults to {default_block_duration} (seconds)")

    module_group = ap.add_argument_group("Upload modules", "Upload modules define how you can upload data (and how it is encrypted). You will need to enable at least one of the following options:")
    module_group.add_argument("--gpg-symmetric", metavar="PASSWORD", help="the client needs to encrypt the file using GPG with the given password and then upload it to 'http://HOST:PORT/gpg'. See README for more details")

    return ap.parse_args()

def main():
    args = parse_args()

    auth_modules = []
    if args.http_basic:
        username, password = args.http_basic
        # @TODO: check length to prevent really weak posswords like "1" or ""
        # @TODO: check password aginst common weak passwords (like "password", "12345678", "admin", "root", "etc")
        auth_modules.append(HttpBasicAuthClientAuthenticator(username, password))
    
    if not auth_modules:
        raise Exception("No authentication module was specified")
    elif len(auth_modules) == 1:
        # We can use the authentication module directly
        authenticator = auth_modules[0]
    else:
        # Create an authenticator handler that will accept requests if at least one authenticator allowed them
        authenticator = MultiClientAuthenticator(auth_modules)

    ip_address_blocker = IpAddressBlocker(args.allow_ips, args.deny_ips, args.block_threshold, args.block_duration)


    modules = []
    if args.gpg_symmetric:
        modules.append(GpgUploadHandler(args.gpg_symmetric))
    if not modules:
        raise Exception("No upload module was specified")
    module_handler = ModuleHandler(modules)

    def handler_class(*args, **kwargs):
        return CustomRequestHandler(*args, authenticator, ip_address_blocker, module_handler, **kwargs)
    # handler_class = functools.partial(CustomRequestHandler, authenticators=[HttpBasicAuthClientAuthenticator("test", "123")])

    test(
        HandlerClass=handler_class,
        ServerClass=ThreadingHTTPServer,
        port=args.http_port,
        bind=args.bind,

    )


if __name__ == "__main__":
    main()
