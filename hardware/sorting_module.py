from common.serial_device import SerialDevice
from common.logger import logger
from common.command_loader import build_command

class SortingModule(SerialDevice):
    CACHE = {
        "left": "854B0000290F006D",       # Turn left
        "middle": "854B0000200F0064",     # Back to middle
        "right": "854B0000090F004D"       # Turn right
    }

    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self._comm_enabled = False

    def send_command(self, key: str):
        if key not in self.CACHE:
            raise ValueError(f"Invalid sorting command '{key}'. Valid options: {list(self.CACHE.keys())}")
        logger.info(f"Sorter: Executing '{key}' command")
        self.send(build_command(self.CACHE[key], add_crc=False))

    def turn_left(self):
        self.send_command("left")

    def back_to_middle(self):
        self.send_command("middle")

    def turn_right(self):
        self.send_command("right")
