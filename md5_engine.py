import struct
import math

class MD5Engine:
    def __init__(self):
        # RFC 1321 Chaining Variables
        self.A, self.B = 0x67452301, 0xefcdab89
        self.C, self.D = 0x98badcfe, 0x10325476
        self.T = [int(0x100000000 * abs(math.sin(i + 1))) & 0xFFFFFFFF for i in range(64)]
        self.S = [7, 12, 17, 22]*4 + [5, 9, 14, 20]*4 + [4, 11, 16, 23]*4 + [6, 10, 15, 21]*4

    def _rotate_left(self, x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    def compute_hash(self, message, init_state=None, init_len=0):
        if isinstance(message, str): message = message.encode('utf-8')
        orig_len = ((len(message) + init_len) * 8) & 0xFFFFFFFFFFFFFFFF
        message += b'\x80'
        while (len(message) + init_len) % 64 != 56: message += b'\x00'
        message += struct.pack('<Q', orig_len)

        if init_state:
            a, b, c, d = init_state
        else:
            a, b, c, d = self.A, self.B, self.C, self.D
            
        for i in range(0, len(message), 64):
            X = list(struct.unpack('<16I', message[i:i+64]))
            aa, bb, cc, dd = a, b, c, d
            for j in range(64):
                if j < 16: f, g = (b & c) | ((~b) & d), j
                elif j < 32: f, g = (d & b) | ((~d) & c), (5 * j + 1) % 16
                elif j < 48: f, g = b ^ c ^ d, (3 * j + 5) % 16
                else: f, g = c ^ (b | (~d)), (7 * j) % 16
                temp = (a + f + self.T[j] + X[g]) & 0xFFFFFFFF
                a, b, c, d = d, (b + self._rotate_left(temp, self.S[j])) & 0xFFFFFFFF, b, c
            a, b, c, d = (a+aa)&0xFFFFFFFF, (b+bb)&0xFFFFFFFF, (c+cc)&0xFFFFFFFF, (d+dd)&0xFFFFFFFF
        return struct.pack('<4I', a, b, c, d).hex()

# PROVIDED COLLISION VECTORS (Exactly 128 bytes)
VEC1_A = "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5bd8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0e99f33420f577ee8ce54b67080a80d1e"
VEC1_B = "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f8955ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbd7280373c5bd8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0e99f33420f577ee8ce54b67080280d1e"