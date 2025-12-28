class twos_complement:


    @staticmethod
    def convert_twos(n, bits=8):

        # signed integer to two's complement
        mask = (1 << bits) - 1
        if n >= 0:
            return n & mask
        
        return ((1 << bits) + n) & mask
    

    @staticmethod
    def convert_signed_int(n, bits=8):

        # two's complement to signed integer
        if n & (1 << (bits - 1)):
            return n - (1 << bits)
        
        return n
    

    @staticmethod
    def to_binary(n, bits=8):

        # get two's complement as binary string
        tc = twos_complement.convert_twos(n, bits)

        return bin(tc)[2:].zfill(bits)
    

    @staticmethod
    def to_hex(n, bits=8):
        
        # get two's complement as hex string
        tc = twos_complement.convert_twos(n, bits)
        hex_chars = (bits + 3) // 4
        return hex(tc)[2:].upper().zfill(hex_chars)