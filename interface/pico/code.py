import usb_hid
import time

# get the custom HID device
hid = usb_hid.devices[0]


while True:
    
    # read from HID stacks (non-blocking)
    report = hid.get_last_received_report(0)
    
    if report:
        print(f"received message : {report} (len={len(report)}, index[0]={report[0]})")
        
        if report[0] == 1:
            debug_len = len(b"debug")
            hid.send_report(bytes(b"debug")+b"\x00"*(64-debug_len), report_id=0)
            
    time.sleep(1)
