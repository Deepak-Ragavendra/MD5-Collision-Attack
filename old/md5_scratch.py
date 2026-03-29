import math

class MD5:
    def __init__(self):
        self.rotate_amounts = [7, 12, 17, 22] * 4 + [5,  9, 14, 20] * 4 + \
                              [4, 11, 16, 23] * 4 + [6, 10, 15, 21] * 4
        self.constants = [int(abs(math.sin(i + 1)) * 2**32) & 0xFFFFFFFF for i in range(64)]
        self.init_values = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476]

    def _left_rotate(self, x, amount):
        return ((x << amount) | (x >> (32 - amount))) & 0xFFFFFFFF

    def hash(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Padding
        orig_len_bits = (len(message) * 8) & 0xFFFFFFFFFFFFFFFF
        message += b'\x80'
        while len(message) % 64 != 56:
            message += b'\x00'
        message += orig_len_bits.to_bytes(8, byteorder='little')

        hash_pieces = list(self.init_values)

        # Process 512-bit chunks
        for chunk_offset in range(0, len(message), 64):
            a, b, c, d = hash_pieces
            chunk = message[chunk_offset:chunk_offset + 64]
            words = [int.from_bytes(chunk[i:i+4], byteorder='little') for i in range(0, 64, 4)]

            for i in range(64):
                if i < 16:
                    f = (b & c) | ((~b) & d)
                    g = i
                elif i < 32:
                    f = (d & b) | ((~d) & c)
                    g = (5 * i + 1) % 16
                elif i < 48:
                    f = b ^ c ^ d
                    g = (3 * i + 5) % 16
                else:
                    f = c ^ (b | (~d))
                    g = (7 * i) % 16

                to_rotate = (a + f + self.constants[i] + words[g]) & 0xFFFFFFFF
                new_b = (b + self._left_rotate(to_rotate, self.rotate_amounts[i])) & 0xFFFFFFFF
                a, b, c, d = d, new_b, b, c

            for i, val in enumerate([a, b, c, d]):
                hash_pieces[i] = (hash_pieces[i] + val) & 0xFFFFFFFF

        return ''.join(format(x, '08x') for x in [
            int.from_bytes(x.to_bytes(4, byteorder='little'), byteorder='big') 
            for x in hash_pieces
        ])