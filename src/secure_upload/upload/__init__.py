# The different upload modules will be housed here
from enum import Enum, auto
from http.server import BaseHTTPRequestHandler
from typing import NamedTuple, Optional


class ModuleStatus(Enum):
    SUCCESS = auto()
    ERROR = auto()
    WRONG_MODULE = auto()


class ModuleResult(NamedTuple):
    status: ModuleStatus
    message: Optional[str]


class UploadModule:
    def __init__(self, additional_headers: dict[str,str] = {}) -> None:
        self.additional_headers = additional_headers

    def handle_GET(self, handler: BaseHTTPRequestHandler) -> ModuleResult:
        raise Exception("This method needs to be overwritten by the subclass")

    def handle_POST(self, handler: BaseHTTPRequestHandler, post_data: dict[bytes,bytes]) -> ModuleResult:
        raise Exception("This method needs to be overwritten by the subclass")
