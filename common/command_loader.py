import yaml
from common.crc import calc_crc16

def load_commands(path='commands.yaml'):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def build_command(command_hex: str, add_crc=True) -> bytes:
    raw = bytes.fromhex(command_hex)
    return raw + calc_crc16(raw) if add_crc else raw