from common.serial_device import SerialDevice
from common.logger import logger
from common.command_loader import build_command

class MotorController(SerialDevice):
    CACHE = {
        "control": "2000",
        "speed": "2001",
        "control_mode": "2006",
        "speed_source": "2007",
        "address": "2008",
        "baudrate": "2009",
        "comm_writable": "200E"
    }

    CONTROL_VALUES = {
        "run_forward": "0001",
        "run_reverse": "0002",
        "stop": "0005",
        "free_stop": "0006",
        "reset": "0007",
        "brake_stop": "0009"
    }

    CONTROL_MODES = {
        "keyboard": "0000",
        "io": "0001",
        "modbus": "0002",
        "switch": "0003"
    }

    def __init__(self, port, baudrate):
        super().__init__(port, baudrate)
        self._comm_enabled = False
        self.set_control_mode("modbus")

    def _verify_hex_integrity(self, hex_str):
        try:
            b = bytes.fromhex(hex_str)
            return hex_str.upper() == b.hex().upper()
        except Exception:
            return False

    def write_cache(self, address_hex: str, value_hex: str):
        if not self._verify_hex_integrity(address_hex):
            raise ValueError(f"Invalid address_hex format: '{address_hex}'")

        if not self._verify_hex_integrity(value_hex):
            raise ValueError(f"Invalid value_hex format: '{value_hex}'")

        if not self._comm_enabled:
            logger.info("Motor: Enabling communication writable mode")
            self._send_write_command(self.CACHE["comm_writable"], "0001")
            self._comm_enabled = True

        self._send_write_command(address_hex, value_hex)

    def _send_write_command(self, address_hex: str, value_hex: str):
        logger.info(f"Motor: Writing value {value_hex} to address {address_hex}")
        cmd = "01" + "06" + address_hex + value_hex
        self.send(build_command(cmd))

    def run_forward(self):
        self.write_cache(self.CACHE["control"], self.CONTROL_VALUES["run_forward"])

    def stop(self):
        self.write_cache(self.CACHE["control"], self.CONTROL_VALUES["stop"])

    def reset(self):
        self.write_cache(self.CACHE["control"], self.CONTROL_VALUES["reset"])

    def set_speed(self, rpm: int):
        if not (0 <= rpm <= 3000):
            raise ValueError("RPM must be between 0 and 3000")
        hex_rpm = f"{rpm:04X}"
        self.write_cache(self.CACHE["speed"], hex_rpm)

    def set_control_mode(self, mode: str):
        if mode not in self.CONTROL_MODES:
            raise ValueError(f"Invalid control mode '{mode}'. Choose from: {list(self.CONTROL_MODES.keys())}")
        self.write_cache(self.CACHE["control_mode"], self.CONTROL_MODES[mode])