import yaml
from common.crc import calc_crc16

def load_commands(path='commands.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def build_command(command_hex: str, add_crc=True) -> bytes:
    raw = bytes.fromhex(command_hex)
    if add_crc:
        result = raw + calc_crc16(raw)
    else:
        result = raw

    # Debug output
    print("=== build_command DEBUG ===")
    print(f"Input HEX:        {command_hex}")
    print(f"Raw Bytes:        {[f'{b:02X}' for b in raw]}")
    if add_crc:
        print(f"CRC Added Bytes:  {[f'{b:02X}' for b in result]}")
    print(f"Final Byte Stream: {result}")
    print("===========================\n")

    return result