from abc import ABC, abstractmethod
import serial
from threading import Lock
from common.error_codes import DeviceError

class SerialDevice(ABC):
    _instances = {}
    _lock = Lock()

    def __new__(cls, port: str, *args, **kwargs):
        with cls._lock:
            if port not in cls._instances:
                instance = super(SerialDevice, cls).__new__(cls)
                cls._instances[port] = instance
            return cls._instances[port]

    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self._last_config = None

    def connect(self):
        try:
            if self.serial and self.serial.is_open:
                if self._last_config != (self.port, self.baudrate, self.timeout):
                    self.serial.baudrate = self.baudrate
                    self._last_config = (self.port, self.baudrate, self.timeout)
            else:
                self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                self._last_config = (self.port, self.baudrate, self.timeout)
        except Exception as e:
            raise DeviceError("E001", str(e))

    def send(self, data: bytes):
        try:
            self.connect()
            self.serial.write(data)
        except Exception as e:
            raise DeviceError("E002", str(e))

    def receive(self, size=128) -> bytes:
        try:
            self.connect()
            return self.serial.read(size)
        except Exception as e:
            raise DeviceError("E003", str(e))

    def close(self):
        try:
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception as e:
            raise DeviceError("E004", str(e))