# boot.py - MUST be in root folder of Pico
import usb_hid

# Enable custom HID device (64-byte reports)
usb_hid.enable(
    (usb_hid.Device(
        report_descriptor=bytes([
            0x06, 0x00, 0xFF,  # Usage Page (Vendor)
            0x09, 0x01,        # Usage (Vendor 1)
            0xA1, 0x01,        # Collection (Application)
            0x15, 0x00,        # Logical Minimum (0)
            0x26, 0xFF, 0x00,  # Logical Maximum (255)
            0x75, 0x08,        # Report Size (8 bits)
            0x95, 0x40,        # Report Count (64 bytes)
            0x09, 0x01,        # Usage (Vendor 1)
            0x81, 0x02,        # Input (Data,Var,Abs)
            0x95, 0x40,        # Report Count (64 bytes)
            0x09, 0x01,        # Usage (Vendor 1)
            0x91, 0x02,        # Output (Data,Var,Abs)
            0xC0               # End Collection
        ]),
        usage_page=0xFF00,  # Vendor-defined
        usage=0x01,         # Vendor usage ID
        report_ids=(0,),    # Enable report ID 0
        in_report_lengths=(64,),  # Input report size
        out_report_lengths=(64,)   # Output report size
    ),)
)

