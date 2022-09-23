import cgi
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

def send_html_response(handler: BaseHTTPRequestHandler, html_str: str):
    http_bytes = bytes(html_str, "utf-8")

    handler.send_response(HTTPStatus.OK)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', len(http_bytes))
    handler.end_headers()
    handler.wfile.write(http_bytes)

def parse_request(headers, body_file_pointer) -> dict:
    ctype, pdict = cgi.parse_header(headers['content-type'])
    if ctype == 'multipart/form-data':
        ### Fix the following error:
        #   [...]
        #   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/cgi.py", line 206, in parse_multipart
        #     boundary = pdict['boundary'].decode('ascii')
        # AttributeError: 'str' object has no attribute 'decode'

        fixed_pdict = {key: value.encode("ascii") for key, value in pdict.items()}
        print(pdict)
        return cgi.parse_multipart(body_file_pointer, fixed_pdict)
    elif ctype == 'application/x-www-form-urlencoded':
        length = int(headers['content-length'])
        request_body_bytes = body_file_pointer.read(length)
        # Parse query string
        return parse_qs(request_body_bytes, keep_blank_values=1)
    else:
        raise Exception(f"Unknown content type: '{ctype}'")   


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

    def do_GET(self) -> None:
        send_html_response(self, "<h1>test page</h1>content")

    def do_POST(self) -> None:
        post_data = parse_request(self.headers, self.rfile)
        print("Received POST data:", post_data)
        send_html_response(self, "Success?")
