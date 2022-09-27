import cgi
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Union
from urllib.parse import parse_qs


def send_http_response(handler: BaseHTTPRequestHandler,
                        status_code: HTTPStatus, # Response status code
                        headers: Union[dict[str,str],list[dict[str,str]]] = [], # Headers in the form of dictionaries. If a list is given the last dictionary has precedence in case of conflicts
                        content: Union[None,str,bytes] = None # The response's body
                    ) -> None:
    
    #################### Handle the response's content ###########################
    if isinstance(content, str):
        response_bytes = bytes(content, "utf-8")
        default_headers = {
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": len(response_bytes),
        }
    elif isinstance(content, bytes):
        response_bytes = content
        default_headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": len(response_bytes),
        }
    else:
        # No contents or contents have a type that is not allowed -> empty response body
        response_bytes = b""
        default_headers = {
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": len(response_bytes),
        }

    ################ Handle the response's headers ####################
    # Merge all the headers
    if isinstance(headers, list):
        for header_map in headers:
            default_headers.update(header_map)
    else:
        default_headers.update(headers)


    ############### Send the response #############################
    handler.send_response(status_code)

    for name, value in sorted(default_headers.items()):
        handler.send_header(name, value)
    handler.end_headers()

    handler.wfile.write(response_bytes)


def parse_request(headers, body_file_pointer) -> dict:
    ctype, pdict = cgi.parse_header(headers['content-type'])
    if ctype == 'multipart/form-data':
        ### Fix the following error:
        #   [...]
        #   File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/cgi.py", line 206, in parse_multipart
        #     boundary = pdict['boundary'].decode('ascii')
        # AttributeError: 'str' object has no attribute 'decode'

        fixed_pdict = {key: value.encode("ascii") for key, value in pdict.items()}
        return cgi.parse_multipart(body_file_pointer, fixed_pdict)
    elif ctype == 'application/x-www-form-urlencoded':
        length = int(headers['content-length'])
        request_body_bytes = body_file_pointer.read(length)
        # Parse query string
        return parse_qs(request_body_bytes, keep_blank_values=1)
    else:
        raise Exception(f"Unknown content type: '{ctype}'")   
