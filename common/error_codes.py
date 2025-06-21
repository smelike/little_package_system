ERROR_CODES = {
    "E001": "Serial port initialization failed.",
    "E002": "Serial port write failed.",
    "E003": "Serial port read failed.",
    "E004": "Serial port already closed or not initialized.",
    "E005": "Unknown device communication error."
}

class DeviceError(Exception):
    def __init__(self, code: str, detail: str = ""):
        self.code = code
        self.message = ERROR_CODES.get(code, "Undefined error code")
        self.detail = detail
        super().__init__(f"[{self.code}] {self.message}: {self.detail}")