import base64
from email import header
from hmac import compare_digest
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import logging
# local
from .http_response import send_http_response

logger = logging.getLogger("ClientAuth")
logger.setLevel(logging.DEBUG)
c_handler = logging.StreamHandler()
c_format = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)


class BaseClientAuthenticator:
    def is_authentication_valid(self, handler: BaseHTTPRequestHandler) -> bool:
        raise Exception("This method needs to be overwritten by subclasses")

    def check_authentication(self, handler: BaseHTTPRequestHandler) -> bool:
        """
        Checks the authentication:
        - Valid: sends nothing, returns True
        - Invalid: sends a 401 response and returns False
        """
        if self.is_authentication_valid(handler):
            return True
        else:
            send_http_response(handler, HTTPStatus.UNAUTHORIZED,
                headers={"WWW-Authenticate": "Basic"},
                content="Authentication required")
            return False


class MultiClientAuthenticator(BaseClientAuthenticator):
    """
    Checks a request with multiple authenticators and accepts it if at least one of them allows the client.
    If no authenticators exist, all request will be denied
    """
    
    def __init__(self, authenticators = list[BaseClientAuthenticator]) -> None:
        super().__init__()
        self.authenticators = authenticators
        if not authenticators:
            logger.warn("MultiClientAuthenticator has no authenticators and will thus reject all requests")

    def is_authentication_valid(self, handler: BaseHTTPRequestHandler) -> bool:
        for auth in self.authenticators:
            if auth.is_authentication_valid(handler):
                return True
        return False


class HttpBasicAuthClientAuthenticator(BaseClientAuthenticator):
    def __init__(self, username: str, password: str) -> None:
        super().__init__()
        # Seems like a reasonable large number, anything larger will likely be impossible to brute force anyways
        self.max_expected_secret_length = 128
        # The null byte should (normally) not be part of the password
        self.pad_char = b"\x00"

        expected_credentials = f"{username}:{password}".encode("utf-8")
        # We pad the credentials beforehand, so that the time required for padding (which likely depends on the value's length) is not leaked
        self.expected_credentials_padded = expected_credentials.ljust(self.max_expected_secret_length, self.pad_char)

    def constant_time_compare(self, user_supplied: bytes) -> bool:
        """
        Compares the supplied credentials with the secret (expected credentials) while trying not to leak any information about the secret (such as its length).
        """
        # Padd the user supplied value to match the (pre-)padded secret's length
        expected_length = max(len(user_supplied), len(self.expected_credentials_padded))
        user_supplied_padded = user_supplied.ljust(expected_length, self.pad_char)

        # Then do a constant time comparison of the two values. The doc's claims:
        # > If a and b are of different lengths, or if an error occurs, a timing attack
        # > could theoretically reveal information about the types and lengths of a and b—but not their values.
        # But we have padded them, so we hopefully do not leak that info
        r = compare_digest(user_supplied_padded, self.expected_credentials_padded)
        # logger.debug(user_supplied_padded)
        # logger.debug(self.expected_credentials_padded)
        # logger.debug(f"Equals? {r}")
        return r


    def is_authentication_valid(self, handler: BaseHTTPRequestHandler) -> bool:
        try:
            auth_header = handler.headers["Authorization"]
            if not auth_header:
                logger.debug("No Authorization header in request")
                return False
            parts = auth_header.split()
            if len(parts) < 2 or parts[0].lower() != "basic":
                # We only want properly formatted HTTP basic authentication
                logger.debug("No valid Basic authentication header")
                return False
            credentials_encoded = parts[1]
            credentials = base64.b64decode(credentials_encoded, validate=True)
            return self.constant_time_compare(credentials)
        except KeyError:
            logger.debug("No Authorization header in request")
            # No auth header
            return False
