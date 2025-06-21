# 📦 Little Package Application — System Overview

## 🔧 Project Background

1. Use **Hiki camera SDK** to read barcodes.  
2. Send the barcode to a **remote server** to fetch cargo information.  
3. During this process, fetch the **stable weight value**.  
4. Trigger the **roller to rotate at a fixed speed**.  
5. The **sorting module camera** detects the cargo box.  
6. When the box reaches different sorting module trigger lines, trigger the module via **MODBUS RTU** using a fixed address.  

## 🛠️ Hardware #1 — Sorting Module

### 📡 Communication Protocol

- Baud rate: **38400**
- Data bits: **8**
- Stop bit: **1**
- Parity: **None**
- Protocol: **Custom MODBUS-like format**

### 🧾 Command Example (Full Frame)

- Turn left: `85 4B 00 00 29 0F 00 6D`  
- Back to middle: `85 4B 00 00 20 0F 00 64`  
- Turn right: `85 4B 00 00 09 0F 00 4D`

### 🔘 Command Types

- `85H` – Single module, expects response  
- `95H` – Single service, no response  
- `FFH` – Broadcast, no response  

### 🧩 Byte Definitions

| Byte  | Description |
|-------|-------------|
| 1     | Command type (85H, 95H, FFH) |
| 2     | Direction + service number |
| 3     | Direct speed (`(byte & 0x7F) * 8`, 200–750 RPM) |
| 4     | Turning speed (`(byte & 0x7F) * 8`, fallback to direct speed) |
| 5     | Turning angle (0–90°) |
| 6     | Delay to return to center (0–1.27s) |
| 7     | Reserved (0) |
| 8     | XOR checksum of Byte2–Byte7 |

### ✅ Response Format

| Byte | Description |
|------|-------------|
| 1    | Start byte: `99H` |
| 2    | Service number |
| 3    | Status flags (stall, overcurrent, I/O) |
| 4    | XOR checksum of Byte2–Byte3 |

## 🛠️ Hardware #2 — Motor Controller (MODBUS RTU)

### 📡 Communication Settings

- Baud rate: **19200**  
- Start bit: **1**, Data bits: **8**, Parity: **None**, Stop bit: **1**

### 📘 MODBUS Data Frame Format

```
[ADDR][CMD][DATA...][CRC_L][CRC_H]
```

- `ADDR` (1 Byte): 0x00 = broadcast, 0x01–0x7F = slave address  
- `CMD` (1 Byte): 0x03 = Read, 0x06 = Write single cache, 0x10 = Write multiple caches  
- `CRC16`: Calculated over `[ADDR + CMD + DATA]`, low byte first

### 🧾 0x06 — Write Single Cache Format

| Field        | Length | Notes |
|--------------|--------|-------|
| Address      | 1 Byte | Slave ID |
| CMD          | 1 Byte | `0x06` |
| Cache Addr   | 2 Bytes| High + low byte |
| Data         | 2 Bytes| High + low byte |
| CRC          | 2 Bytes| CRC16_L + CRC16_H |

### 📬 Example Commands

| Description                   | Command                      | Address |
|-------------------------------|------------------------------|---------|
| Run forward                   | `01 06 20 00 00 01 43 CA`    | 2000H |
| Run reverse                   | `01 06 20 00 00 02 03 CB`    | 2000H |
| Stop                          | `01 06 20 00 00 05 42 09`    | 2000H |
| Reset                         | `01 06 20 00 00 07 C3 C8`    | 2000H |
| Set speed to 3000 RPM         | `01 06 20 01 0B B8 D4 88`    | 2001H |
| Enable writable communication | `01 06 20 0E 00 01 09 22`    | 200EH |

## 🧠 Cache Register Summary

| Address | Description         | Values |
|---------|---------------------|--------|
| 2000H   | Operation Control   | `0001`, `0002`, `0005`, etc. |
| 2001H   | Speed Setting       | 0–3000 RPM |
| 2006H   | Control Mode        | `0` keyboard, `1` IO, `2` modbus, `3` switch |
| 2007H   | Speed Source        | `3` = MODBUS |
| 2008H   | Slave Address       | 1–127 |
| 2009H   | Baud Rate           | 0 = 1200, 4 = 19200 |
| 200EH   | Enable Communication| `0001` to enable |

## 🧪 Exception Codes

| Code | Meaning |
|------|---------|
| 0x01 | Illegal Function |
| 0x02 | Illegal Address |
| 0x03 | Illegal Data Value |
| 0x04 | Operation Failed |
| 0x05 | Password Error |
| 0x06 | Data Frame Error |

## 💻 Development Task (Python 3.8)

1. Design the directory structure.
2. Create classes for each hardware controller.
3. Use an abstract base class for serial device abstraction.
4. Implement logging for device operations.
5. Write unit tests for all functions and classes.