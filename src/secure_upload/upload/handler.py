from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Callable
# local
from . import ModuleResult, UploadModule, ModuleStatus
from ..http_response import send_http_response


class ModuleHandler:
    def __init__(self, modules: list[UploadModule]) -> None:
        if not modules:
            raise Exception("ModuleHandler has been given an empty list of upload modules")
        self.modules = modules

    def handle_GET(self, handler: BaseHTTPRequestHandler) -> None:
        self.handle_generic(handler, lambda module, handler: module.handle_GET(handler))

    def handle_POST(self, handler: BaseHTTPRequestHandler, post_data: dict[bytes,bytes]) -> ModuleResult:
        self.handle_generic(handler, lambda module, handler: module.handle_POST(handler, post_data))


    def handle_generic(self, handler: BaseHTTPRequestHandler, fn_let_module_handle_the_request: Callable[[UploadModule,BaseHTTPRequestHandler],ModuleResult]):
        for module in self.modules:
            result = fn_let_module_handle_the_request(module, handler)
            if result.status == ModuleStatus.SUCCESS:
                # Module processed the request successfully
                send_http_response(handler, HTTPStatus.OK, headers=module.additional_headers, content=result.message)
            elif result.status == ModuleStatus.ERROR:
                # Module processed the request successfully
                send_http_response(handler, HTTPStatus.INTERNAL_SERVER_ERROR, headers=module.additional_headers, content=result.message)
            elif result.status == ModuleStatus.WRONG_MODULE:
                # Module processed the request successfully
                send_http_response(handler, HTTPStatus.NOT_FOUND, headers=module.additional_headers, content="Invalid request or the required module is not enabled")
            else:
                raise Exception(f"Unexpected status code returned by module '{type(module).__name__}'")


