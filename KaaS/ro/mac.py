import aes


# SBoxes with entries from g^i (mod p) for protection against differential
# cryptanalysis. With p=257 and g=177
sbox = []
for i in range(2, 258):
    sbox.append(pow(177, i, 257))
sbox[sbox.index(256)] = 0

# This key is part of the MAC, exchanging it will break the MAC. You will
# lose certification! We paid a lot from our military budget to certify
# this MAC!
const_key = '\xf3a\xee\xd0\\\x1d\xb5\x06\xed\xa9\xdb\xf5B\xccPF'

# More constants for the MAC, again exchanging them will lose certification!
iv1 = '6\xe1U\xd7\x11_p\x81'
iv2 = '\x85\x9b?\x08\x9b~}R'

cipher = aes.AES(const_key)


def str2lst(s):
    return [ord(x) for x in s]


def lst2str(l):
    return ''.join(chr(x) for x in l)


def xorbytes(str1, str2):
    if len(str1) != len(str2):
        raise ValueError('Different number of bytes')
    return lst2str(ord(x) ^ ord(y) for x, y in zip(str1, str2))


def compress(a, b):
    out_block = lst2str(cipher.encrypt(str2lst(a + b)))
    return out_block[:8], out_block[8:]


def finalize(a, b, block):
    a2, b2 = compress(b, block)
    h = bytearray(a2 + b2 + a)
    for i in range(14):
        for j in range(len(h)):
            h[j] = sbox[h[j]]
        tmp = h[0]
        for j in range(1, len(h)):
            h[j - 1] = ((h[j - 1] << 4) & 0xff) | ((h[j] & 0xf0) >> 4)
        h[-1] = ((h[-1] << 4) & 0xff) | ((tmp & 0xf0) >> 4)
    return bytes(h)


def fast_wide_pipe(blocks, a1=iv1, b1=iv2):
    a2, b2 = a1, b1
    for block in blocks[:-1]:
        a2, b2 = compress(b1, block)
        b1 = xorbytes(a1, b2)
        a1 = a2
    return finalize(a2, b1, blocks[-1])


def split_blocks(message):
    pad_size = 8 - (len(message) % 8)
    if pad_size == 0:
        pad_size = 8
    message += '\x01' + '\x00' * (pad_size - 1)
    return [message[i:i + 8] for i in range(0, len(message), 8)]


def aes_mac(key, message):
    key = fast_wide_pipe(split_blocks(key))
    blocks = [key[0:8], key[8:16], key[16:24]] + split_blocks(message)
    mac = fast_wide_pipe(blocks)
    return mac


def constant_time_compare(s1, s2):
    if len(s1) != len(s2):
        return False
    result = 0
    for a, b in zip(s1, s2):
        result |= ord(a) ^ ord(b)
    return result == 0