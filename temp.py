import crcmod, serial

class asd_906b(serial.Serial):

    def __init__(self, port, logging=False):
        
        self.logging = logging
        self._enable_flag = False
        self._voltage = 0.1
        
        self.packet_port  = f"{port:02}"
        self.packet_read  = f"{0x11:02x}"
        self.packet_write = f"{0x10:02x}"
        self.local_addr = "01"
        
        try:
            serial.Serial.__init__(
                self,
                port=f"COM{self.packet_port}",
                baudrate=115200,
                bytesize=8,
                parity="N",
                stopbits=1,
                timeout=3
                )
            
            print(f"initialized the asd-906b connection to COM{port}")
        except:
            print(f"failed to initialize asd-906b")


    def crc_generate(self, value):
        
        # CRC-16 (Modbus) generator

        crc16 = crcmod.mkCrcFun(
            0x18005,
            rev=True,
            initCrc=0xFFFF,
            xorOut=0x0000
            )
        
        byte_array = bytes.fromhex(value)
        checksum   = crc16(byte_array)

        second_crc = str(f"{checksum:04X}")[0:2]
        first_crc = str(f"{checksum:04X}")[2:4]
        
        return [first_crc, second_crc]


    def send_packet(self, packet):

        ret_crc16 = self.crc_generate(" ".join(packet))
        packet.extend(ret_crc16)
        
        for byte16 in packet:
            self.write(bytes.fromhex(byte16))
        

    @property
    def enable(self):

        if self._enable_flag:
            pass

        else:
            self._enable_flag = True
            msb, lsb = self.conv_voltage(self._voltage)

            ps_state = "01" # unchanged
            curr_state = "00" # unchanged

            module_info = [self.local_addr, "11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
            
            ret_crc = self.crc_generate(" ".join(module_info))
            module_info.extend(ret_crc)

            self.send_packet(module_info)
    

    @property
    def disable(self):

        self._enable_flag = False
        # msb, lsb = self.conv_voltage(self._voltage)
        msb, lsb = self.conv_voltage(0.1)

        ps_state = "02" # unchanged
        curr_state = "00" # unchanged

        module_info = [self.local_addr, "11", "10", "08", ps_state, msb, lsb, curr_state, "00", "00", "00", "00"]
        
        ret_crc = self.crc_generate(" ".join(module_info))
        module_info.extend(ret_crc)

        self.send_packet(module_info)
    
    
    def receive_packet(self):
        try:
            # Read the incoming data
            incoming_data = self.read(12)  # Adjust the number of bytes to read as necessary
            if len(incoming_data) < 12:
                print("Received incomplete packet")
                return None
            
            # Convert bytes to hex strings
            data_hex = incoming_data.hex().upper()
            
            # Split the data into a list
            packet = [data_hex[i:i+2] for i in range(0, len(data_hex), 2)]
            
            # Extract the CRC from the packet
            received_crc = packet[-2:]  # Last two bytes are the CRC
            data_without_crc = packet[:-2]  # All but the last two bytes
            
            # Calculate CRC for the received data
            calculated_crc = self.crc_generate(" ".join(data_without_crc))
            
            # Validate the CRC
            if received_crc == calculated_crc:
                print("Received valid packet:", packet)
                return packet  # Return the valid packet
            else:
                print("Invalid CRC, packet discarded")
                return None
        except serial.SerialException as e:
            print(f"Serial error: {e}")
        except Exception as e:
            print(f"Error receiving packet: {e}")