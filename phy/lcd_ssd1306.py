# olde ssd1306
# resolution : 128 x 32

# page addressing mode
# - ssd1306 uses pages (8 rows each, 32/8=4 pages)
# - buffer Size : since each page has 128 columns, the total buffer size is 128×4=512 bytes
# - each byte in the buffer represents 8 vertical pixels in a column

# commands are sent with a control byte of 0x00
# data is sent with a control byte of 0x40


from interface.i2c_bridge.cp2112 import cp2112
from time import sleep as delay
import os, sys

i2c_addr = 0x3C
bus = cp2112()

INIT_COMMANDS = [
    0xAE,  # Display OFF
    0x20, 0x00,  # Set Memory Addressing Mode to Horizontal
    0xB0,  # Set Page Start Address for Page Addressing Mode
    0xC8,  # COM Output Scan Direction
    0x00,  # Set Lower Column Start Address
    0x10,  # Set Higher Column Start Address
    0x40,  # Set Display Start Line
    0x81, 0x7F,  # Set Contrast Control
    0xA1,  # Segment Re-map
    0xA6,  # Normal Display
    0xA8, 0x1F,  # Set Multiplex Ratio (for 128x32)
    0xD3, 0x00,  # Set Display Offset
    0xD5, 0x80,  # Set Display Clock Divide Ratio/Oscillator Frequency
    0xD9, 0xF1,  # Set Pre-charge Period
    0xDA, 0x02,  # Set COM Pins Hardware Configuration (for 128x32)
    0xDB, 0x40,  # Set VCOMH Deselect Level
    0x8D, 0x14,  # Enable Charge Pump
    0xAF  # Display ON
]

def send_command(command):
    bus.i2c_write_multiple_byte(i2c_addr, 0x00, [command])

def send_data(data):
    bus.i2c_write_multiple_byte(i2c_addr, 0x40, data)

# Initialize the display
for cmd in INIT_COMMANDS:
    send_command(cmd)

# Clear the display buffer (128x32 = 512 bytes)
buffer = [0x00] * 512
for i in range(4):  # 4 pages for 32 pixels
    send_command(0xB0 + i)  # Set page address
    send_command(0x00)  # Set lower column start address
    send_command(0x10)  # Set higher column start address
    send_data(buffer[i * 128:(i + 1) * 128])

# Example: Light up a single pixel in the first byte
buffer[0] = 0xFF  # First 8 pixels in the first column
send_data(buffer[:128])  # Send the first page (128 bytes)

print("Display initialized and updated.")
