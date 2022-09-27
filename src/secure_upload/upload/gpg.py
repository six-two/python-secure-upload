import subprocess
from http.server import BaseHTTPRequestHandler
import os
import traceback
# local
from . import UploadModule, ModuleResult, ModuleStatus
from ..http_response import parse_request

FIELD_NAME = b"gpg"
FILE_NAME = b"filename"

class GpgUploadHandler(UploadModule):
    def __init__(self, symmetric_key: str) -> None:
        super().__init__()
        self.gpg_executeable = "gpg"
        self.symmetric_key = symmetric_key

    def handle_GET(self, handler: BaseHTTPRequestHandler) -> ModuleResult:
        return ModuleResult(ModuleStatus.WRONG_MODULE, None)

    def handle_POST(self, handler: BaseHTTPRequestHandler, post_data: dict[bytes,bytes]) -> ModuleResult:
        # Normalize path
        path = handler.path.lower()
        while path.endswith("/"):
            path = path[:-1]

        if path in ["", "/gpg"]:
            try:
                if FIELD_NAME in post_data:
                    file_name = post_data.get(FILE_NAME, "unnamed")
                    # Prevent path traversal attacks
                    file_name =  os.path.basename(file_name)

                    try:
                        self.handle_file(file_name, post_data[FIELD_NAME])
                        return ModuleResult(ModuleStatus.SUCCESS, "File uploaded and decrypted")
                    except Exception:
                        return ModuleResult(ModuleStatus.ERROR, f"Failed to decrypt file with GPG. Did you use the right password for the symmetric encryption?")

            except Exception:
                traceback.print_exc()

            if path == "":
                return ModuleResult(ModuleStatus.WRONG_MODULE, None)
            else:
                return ModuleResult(ModuleStatus.ERROR, f"Missing POST parameter: '{FIELD_NAME.decode()}'")
        else:
            return ModuleResult(ModuleStatus.WRONG_MODULE, None)

    def handle_file(self, file_name: str, contents: bytes) -> None:
        command = [self.gpg_executeable, "-d", "--pinentry-mode", "loopback", "--passphrase", self.symmetric_key, "-o", f"/tmp/TODO_change_me_{file_name}"]
        print("Running command:", command)
        subprocess.run(command, input=contents, check=True)
