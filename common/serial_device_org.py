from abc import ABC, abstractmethod
import serial

class SerialDevice(ABC):
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 0.5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)

    def send(self, data: bytes):
        self.serial.write(data)

    def receive(self, size=128) -> bytes:
        return self.serial.read(size)

    def close(self):
        if self.serial:
            self.serial.close()