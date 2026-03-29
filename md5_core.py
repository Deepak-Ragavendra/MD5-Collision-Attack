import struct
import math

class MD5Engine:
    def __init__(self):
        # Initial chaining variables (RFC 1321)
        self.IV = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)
        # Constants from Sine function
        self.T = [int(0x100000000 * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]
        # Rotation amounts
        self.S = [7, 12, 17, 22]*4 + [5, 9, 14, 20]*4 + [4, 11, 16, 23]*4 + [6, 10, 15, 21]*4

    def _left_rotate(self, x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    def compute_hash(self, message, init_state=None, init_len=0):
        if isinstance(message, str): message = message.encode('utf-8')
        orig_len_bits = ((len(message) + init_len) * 8) & 0xFFFFFFFFFFFFFFFF
        
        # Padding logic
        message += b'\x80'
        while (len(message) + init_len) % 64 != 56: message += b'\x00'
        message += struct.pack('<Q', orig_len_bits)

        if init_state:
            a, b, c, d = init_state
        else:
            a, b, c, d = self.IV
        # Main compression loop
        for i in range(0, len(message), 64):
            block = message[i:i+64]
            X = list(struct.unpack('<16I', block))
            AA, BB, CC, DD = a, b, c, d
            for j in range(64):
                if j < 16: f, g = (b & c) | ((~b) & d), j
                elif j < 32: f, g = (d & b) | ((~d) & c), (5 * j + 1) % 16
                elif j < 48: f, g = b ^ c ^ d, (3 * j + 5) % 16
                else: f, g = c ^ (b | (~d)), (7 * j) % 16
                
                sum_rot = (a + f + self.T[j] + X[g]) & 0xFFFFFFFF
                a, b, c, d = d, (b + self._left_rotate(sum_rot, self.S[j])) & 0xFFFFFFFF, b, c
            a, b, c, d = (a+AA)&0xFFFFFFFF, (b+BB)&0xFFFFFFFF, (c+CC)&0xFFFFFFFF, (d+DD)&0xFFFFFFFF

        return struct.pack('<4I', a, b, c, d).hex()