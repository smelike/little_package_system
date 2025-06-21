from common.serial_device import SerialDevice
from common.logger import logger
from common.command_loader import load_commands, build_command

class SortingModule(SerialDevice):
    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self.commands = load_commands()["hardware_1_sorting_module"]

    def turn_left(self):
        logger.info("Sorter: Turning left")
        self.send(build_command(self.commands["turn_left"], add_crc=False))

    def back_to_middle(self):
        logger.info("Sorter: Returning to middle")
        self.send(build_command(self.commands["back_to_middle"], add_crc=False))

    def turn_right(self):
        logger.info("Sorter: Turning right")
        self.send(build_command(self.commands["turn_right"], add_crc=False))