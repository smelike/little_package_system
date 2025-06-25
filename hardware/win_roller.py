import serial
from typing import Tuple

class WinRoller:
    BAUDRATE = 38400
    STOP_BITS = 1
    VERIFY_BIT = 'None'
    ADDRESS = 0x01
    PORT = 'COM3'  # /dev/ttyUSB0 change as needed

    CMD_WRITE_COIL = 0x05
    CMD_WRITE_REGISTER = 0x06

    # Coil (bdata) map
    COIL_MAP = {
        'enable_run': 0x00,
        'direction': 0x01,
        'loop_mode': 0x02,
        'run_mode': 0x03,
        'restart_mode': 0x04
    }

    # Register (wdat) map
    REGISTER_MAP = {
        'rpm': 0x00,
        'speed_up': 0x01,
        'slow_down': 0x02,
        'total_current': 0x03,
        'ab_current': 0x04
    }

    def __init__(self, port: str = PORT):
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
        data = bytearray()
        data.append(self.ADDRESS)
        data.append(cmd)
        data += addr.to_bytes(2, 'big')
        data += value.to_bytes(2, 'big')
        data += self._crc16(data)
        return bytes(data)

    def _send_and_log(self, command: bytes, description: str) -> bytes:
        self.serial.write(command)
        response = self.serial.read(8)
        log_entry = f"COMMAND ({description}): {command.hex().upper()}\nRESPONSE: {response.hex().upper()}\n\n"
        print(log_entry.strip())
        self.log_file.write(log_entry)
        self.log_file.flush()
        return response

    # --- Coil setters (bdata) ---
    def set_coil(self, name: str, on: bool) -> bytes:
        addr = self.COIL_MAP[name]
        value = 0xFF00 if on else 0x0000
        cmd = self._build_command(self.CMD_WRITE_COIL, addr, value)
        return self._send_and_log(cmd, f"set_coil {name}={'ON' if on else 'OFF'}")

    # --- Register setters (wdat) ---
    def set_register(self, name: str, value: int) -> bytes:
        addr = self.REGISTER_MAP[name]
        cmd = self._build_command(self.CMD_WRITE_REGISTER, addr, value)
        return self._send_and_log(cmd, f"set_register {name}={value}")

    # --- Action functions ---
    def start_with_rpm_and_direct(self, rpm: int, reverse: bool) -> Tuple[bytes, bytes, bytes]:
        resp1 = self.set_register('rpm', rpm)
        resp2 = self.set_coil('direction', reverse)
        resp3 = self.set_coil('enable_run', True)
        return resp1, resp2, resp3

    def reset(self, auto: bool = False) -> bytes:
        return self.set_coil('restart_mode', auto)

    def act_set_mode(self, io_mode: bool) -> bytes:
        return self.set_coil('run_mode', io_mode)

    def act_stop(self) -> bytes:
        return self.set_coil('enable_run', False)

    def close(self):
        self.serial.close()
        self.log_file.close()


if __name__ == '__main__':
    wr = WinRoller()
    try:
        wr.set_coil('enable_run', True)
        wr.set_register('rpm', 1000)
        wr.start_with_rpm_and_direct(1000, False)
    finally:
        wr.close()
#hardware\win_roller.py