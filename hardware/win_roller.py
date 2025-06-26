import serial
from typing import Tuple

class WinRoller:
    """
    Modbus RTU control for Win Roller device.
    """

    BAUDRATE = 38400
    STOP_BITS = 1
    VERIFY_BIT = 'None'
    ADDRESS = 0x01
    PORT = '/dev/ttyUSB0'  # Update to your actual port

    CMD_WRITE_COIL = 0x05
    CMD_WRITE_REGISTER = 0x06

    # Coil (bdata) address map
    COIL_MAP = {
        'enable_run': 0x00,    # bdata0.0
        'direction': 0x01,     # bdata0.1
        'loop_mode': 0x02,     # bdata0.2
        'run_mode': 0x03,      # bdata0.3
        'restart_mode': 0x04   # bdata0.4
    }

    # Register (wdat) address map
    REGISTER_MAP = {
        'rpm': 0x00,
        'speed_up': 0x01,
        'slow_down': 0x02,
        'total_current': 0x03,
        'ab_current': 0x04
    }

    def __init__(self, port: str = PORT):
        """
        Initialize serial port and log file.
        """
        self.serial = serial.Serial(
            port=port,
            baudrate=self.BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=self.STOP_BITS,
            timeout=1
        )
        self.log_file = open("modbus_log.txt", "w")

    def _crc16(self, data: bytes) -> bytes:
        """
        Compute CRC16 (Modbus standard).
        """
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, 'little')

    def _build_command(self, cmd: int, addr: int, value: int) -> bytes:
        """
        Build Modbus RTU command.
        :param cmd: Modbus command code (e.g., 0x05 or 0x06)
        :param addr: Register or coil address
        :param value: Value to write
        """
        data = bytearray()
        data.append(self.ADDRESS)
        data.append(cmd)
        data += addr.to_bytes(2, 'big')
        data += value.to_bytes(2, 'big')
        data += self._crc16(data)
        return bytes(data)

    def _send_and_log(self, command: bytes, description: str) -> bytes:
        """
        Send command via serial and log the result.
        :param command: The full Modbus command bytes
        :param description: Description of the action
        """
        self.serial.write(command)
        response = self.serial.read(8)
        log_entry = f"COMMAND ({description}): {command.hex().upper()}\nRESPONSE: {response.hex().upper()}\n\n"
        print(log_entry.strip())
        self.log_file.write(log_entry)
        self.log_file.flush()
        return response

    def set_coil(self, name: str, value: int) -> bytes:
        """
        Write to a digital coil.
        :param name: Coil name as in COIL_MAP
        :param value: 0 or 1 (1 will be encoded as FF00)
        """
        assert name in self.COIL_MAP, f"Invalid coil name: {name}"
        assert value in (0, 1), "Coil value must be 0 or 1"
        addr = self.COIL_MAP[name]
        encoded_value = 0xFF00 if value == 1 else 0x0000
        cmd = self._build_command(self.CMD_WRITE_COIL, addr, encoded_value)
        return self._send_and_log(cmd, f"set_coil {name}={value}")

    def set_register(self, name: str, value: int) -> bytes:
        """
        Write to a holding register.
        :param name: Register name as in REGISTER_MAP
        :param value: Integer value to write
        """
        assert name in self.REGISTER_MAP, f"Invalid register name: {name}"
        addr = self.REGISTER_MAP[name]
        cmd = self._build_command(self.CMD_WRITE_REGISTER, addr, value)
        return self._send_and_log(cmd, f"set_register {name}={value}")

    def start_with_rpm_and_direct(self, rpm: int, reverse: bool) -> Tuple[bytes, bytes, bytes]:
        """
        Start roller with proper setup sequence.
        :param rpm: Speed in RPM to set
        :param reverse: Direction flag (True for reverse, False for forward)
        :return: Tuple of response bytes from rpm, direction, enable
        """
        self.set_coil('run_mode', 0)  # Step 1: 485 mode
        resp1 = self.set_register('rpm', rpm)  # Step 2: Set RPM
        resp2 = self.set_coil('direction', 1 if reverse else 0)  # Step 3: Direction
        resp3 = self.set_coil('enable_run', 1)  # Step 4: Enable
        return resp1, resp2, resp3

    def reset(self, auto: bool = False) -> bytes:
        """
        Trigger manual or auto reset.
        :param auto: True for auto reset, False for manual
        """
        return self.set_coil('restart_mode', 1 if auto else 0)

    def act_set_mode(self, io_mode: bool) -> bytes:
        """
        Switch between I/O mode and 485 mode.
        :param io_mode: True for I/O mode, False for 485
        """
        return self.set_coil('run_mode', 1 if io_mode else 0)

    def act_stop(self) -> bytes:
        """
        Stop roller.
        """
        return self.set_coil('enable_run', 0)

    def close(self):
        """
        Clean up serial and log file.
        """
        self.serial.close()
        self.log_file.close()


if __name__ == '__main__':
    wr = WinRoller()
    try:
        wr.start_with_rpm_and_direct(1000, False)
    finally:
        wr.close()
        print("WinRoller test completed.")
        