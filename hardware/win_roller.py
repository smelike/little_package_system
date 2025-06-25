from typing import Tuple

class WinRoller:
    BAUDRATE = 38400
    STOP_BITS = 1
    VERIFY_BIT = 'None'
    ADDRESS = 0x01

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

    # --- Coil setters (bdata) ---
    def set_coil(self, name: str, on: bool) -> bytes:
        addr = self.COIL_MAP[name]
        value = 0xFF00 if on else 0x0000
        return self._build_command(self.CMD_WRITE_COIL, addr, value)

    # --- Register setters (wdat) ---
    def set_register(self, name: str, value: int) -> bytes:
        addr = self.REGISTER_MAP[name]
        return self._build_command(self.CMD_WRITE_REGISTER, addr, value)

    # --- Action functions ---
    def start_with_rpm_and_direct(self, rpm: int, reverse: bool) -> Tuple[bytes, bytes, bytes]:
        cmds = [
            self.set_register('rpm', rpm),
            self.set_coil('direction', reverse),
            self.set_coil('enable_run', True)
        ]
        return tuple(cmds)

    def reset(self, auto: bool = False) -> bytes:
        return self.set_coil('restart_mode', auto)

    # Extra action templates
    def act_set_mode(self, io_mode: bool) -> bytes:
        return self.set_coil('run_mode', io_mode)

    def act_stop(self) -> bytes:
        return self.set_coil('enable_run', False)


if __name__ == '__main__':
    wr = WinRoller()
    # Example usage
    print(wr.set_coil('enable_run', True).hex().upper())
    print(wr.set_register('rpm', 1000).hex().upper())
    for cmd in wr.start_with_rpm_and_direct(1000, False):
        print(cmd.hex().upper())
