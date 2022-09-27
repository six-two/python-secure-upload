from . import UploadModule, ModuleResult, ModuleStatus
from http.server import BaseHTTPRequestHandler


class GpgUploadHandler(UploadModule):
    def __init__(self, symmetric_key: str) -> None:
        super().__init__()
        self.gpg_executeable = "gpg"
        self.symmetric_key = symmetric_key

    def handle_GET(self, handler: BaseHTTPRequestHandler) -> ModuleResult:
        return ModuleResult(ModuleStatus.WRONG_MODULE, None)

    def handle_POST(self, handler: BaseHTTPRequestHandler) -> ModuleResult:
        if handler.path.lower() in ["", "/", "/gpg", "/gpg/"]:
            return ModuleResult(ModuleStatus.ERROR, "Not implemented yet")
        else:
            return ModuleResult(ModuleStatus.WRONG_MODULE, None)


