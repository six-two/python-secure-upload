from asyncio.log import logger
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import logging

# local
from secure_upload.upload.handler import ModuleHandler
from .client_auth import BaseClientAuthenticator, MultiClientAuthenticator
from .ip_blocking import IpAddressBlocker
from .http_response import parse_request

logger = logging.getLogger("Server")
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_format = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


class CustomRequestHandler(BaseHTTPRequestHandler):
    # Try to make fingerprinting a bit harder by not using the default Python error message
    error_message_format = ""

    ###### Start: Remove the value from the Server HTTP header
    # Remove the BaseHTTP/0.6 part
    server_version = ""

    # Remove the rest of the server header
    def version_string(self) -> str:
        return ""
    
    # Prevent sending the (empty) server header
    def send_header(self, keyword: str, value: str) -> None:
        if keyword.lower() != "server":
            return super().send_header(keyword, value)
    ###### End: Remove the value from the Server HTTP header

    def __init__(self, request: bytes, client_address: tuple[str, int], server,
        authenticator: BaseClientAuthenticator, ip_address_blocker: IpAddressBlocker, upload_module_handler: ModuleHandler) -> None:
        # For some reason it needs to be called before the superclass constructor.
        # I think the constructor calls the do_GET (and similar methods), which then access the not yet defined fields
        self.authenticator = authenticator
        self.ip_address_blocker = ip_address_blocker
        self.upload_module_handler = upload_module_handler

        # Check the client IP address.
        # @TODO: Should I try to add load-balancer support? Then I would need to parse the X-Forwarded-For header (in do_*)
        #        And also make sure, that clients can not spoof the header (by checking that the request came from the LB's IP address)
        self.client_ip = client_address[0]

        # Update blocks (which may drop temporary blocks), before cheking if the address is blocked
        ip_address_blocker.update_blocks()
        if ip_address_blocker.is_blocked(self.client_ip):
            # @TODO: What should I do? skip calling the supercalss constructor to prevent processing the request?
            # Or do i need to close the connection / send a response?

            # This seems to just reset the connection:
            # $ curl 'http://localhost:8000/' -u "test:12"
            # curl: (56) Recv failure: Connection reset by peer
            logger.debug(f"Dropping request from blocked IP address {self.client_ip}")
            return

        super().__init__(request, client_address, server)

    def check_authentication(self) -> bool:
        self.ip_address_blocker.update_blocks()

        if self.authenticator.check_authentication(self):
            return True
        else:
            # Log the failed authentication attempts
            self.ip_address_blocker.increase_failed_auth_count(self.client_ip)
            return False

    def do_GET(self) -> None:
        if self.check_authentication():
            self.upload_module_handler.handle_GET(self)

    def do_POST(self) -> None:
        if self.check_authentication():
            post_data = parse_request(self.headers, self.rfile)
            logger.debug(f"POST data: {post_data}")
            self.upload_module_handler.handle_POST(self, post_data)
