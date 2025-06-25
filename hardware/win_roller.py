import serial
from typing import Tuple

class WinRoller:
    BAUDRATE = 38400
    STOP_BITS = 1
    VERIFY_BIT = 'None'
    ADDRESS = 0x01
    PORT = '/dev/ttyUSB0'  # change as needed

    CMD_WRITE_COIL = 0x05
    CMD_WRITE_REGISTER = 0x06

    # Coil (bdata) map
    COIL_MAP = {
        'enable_run': 0x00,   # bdata0.0
        'direction': 0x01,    # bdata0.1
        'loop_mode': 0x02,    # bdata0.2
        'run_mode': 0x03,     # bdata0.3
        'restart_mode': 0x04  # bdata0.4
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
    def set_coil(self, name: str, value: int) -> bytes:
        addr = self.COIL_MAP[name]
        cmd = self._build_command(self.CMD_WRITE_COIL, addr, value)
        return self._send_and_log(cmd, f"set_coil {name}={value}")

    # --- Register setters (wdat) ---
    def set_register(self, name: str, value: int) -> bytes:
        addr = self.REGISTER_MAP[name]
        cmd = self._build_command(self.CMD_WRITE_REGISTER, addr, value)
        return self._send_and_log(cmd, f"set_register {name}={value}")

    # --- Action functions ---
    def start_with_rpm_and_direct(self, rpm: int, reverse: bool) -> Tuple[bytes, bytes, bytes]:
        # Step 1: Set 485 mode (bdata0.3 set to 0)
        self.set_coil('run_mode', 0)
        # Step 2: Set RPM
        resp1 = self.set_register('rpm', rpm)
        # Step 3: Set direction (bdata0.1)
        resp2 = self.set_coil('direction', 1 if reverse else 0)
        # Step 4: Enable run (bdata0.0 set to 1)
        resp3 = self.set_coil('enable_run', 1)
        return resp1, resp2, resp3

    def reset(self, auto: bool = False) -> bytes:
        return self.set_coil('restart_mode', 1 if auto else 0)

    def act_set_mode(self, io_mode: bool) -> bytes:
        return self.set_coil('run_mode', 1 if io_mode else 0)

    def act_stop(self) -> bytes:
        return self.set_coil('enable_run', 0)

    def close(self):
        self.serial.close()
        self.log_file.close()


if __name__ == '__main__':
    wr = WinRoller()
    try:
        wr.start_with_rpm_and_direct(1000, False)
    finally:
        wr.close()
