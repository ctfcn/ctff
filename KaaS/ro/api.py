r"""
API for encoding dictionaries and securing with a MAC.

A dictionary is encoded by a sequence of key, value entries. For example:
"foo" 7 "qux" False 42 None
will be: {"foo": 7, "qux": False, 42: None}

Individual types are encoded as follows:

None:
\x00 -- Just one zero byte for None

Strings:
\x01 \xSS \xSS \xAB \xCD \xEF -- where
  \x01 = String type
  \xSS \XSS = Size (2 byte big endian, unsigned)
  \xAB \xCD \xEF = A string of given size UTF-8 encoded

Integers:
\x02 \xAA \xAA \xAA \xAA -- where
  \x02 = Integer type
  \xAA \xAA \xAA \xAA = Integer (4 byte big endian, signed)

Bool:
\x03 \xAA -- where
  \x03 = Bool type
  \xAA = 00 for False, 01 for True

So the dictionary mentioned above would be:

\x01 \x00 \x03 \x66 \x6f \x6f  -- "foo"
\x02 \x00 \x00 \x00 \x07       -- 7
\x01 \x00 \x03 \x71 \x75 \x78  -- "qux"
\x03 \x00                      -- False
\x02 \x00 \x00 \x00 \x2a       -- 42
\x00                           -- None

This byte sequence is then prefixed by a 24 byte MAC.
"""

import struct
import cStringIO as StringIO

from mac import aes_mac, constant_time_compare


TYPE_NONE = 0
TYPE_STR = 1
TYPE_INT = 2
TYPE_BOOL = 3


def encode_parameters(secret_key, parameters):
    buf = StringIO.StringIO()
    for key, value in parameters.iteritems():
        buf.write(_encode_obj(key))
        buf.write(_encode_obj(value))
    data = buf.getvalue()
    return aes_mac(secret_key, data) + data


def decode_parameters(secret_key, data, verify_mac=True):
    if len(data) < 24:
        raise ValueError('Invalid data')
    given_mac, real_data = data[:24], data[24:]
    real_mac = aes_mac(secret_key, real_data)
    if verify_mac and not constant_time_compare(real_mac, given_mac):
        raise ValueError('Invalid mac')
    return _decode_data(real_data)


def _encode_none():
    return struct.pack('!B', TYPE_NONE)


def _encode_str(s):
    return struct.pack('!BH', TYPE_STR, len(s)) + s


def _encode_int(i):
    return struct.pack('!Bi', TYPE_INT, i)


def _encode_bool(b):
    return struct.pack('!BB', TYPE_BOOL, 1 if b else 0)


def _encode_obj(x):
    if x is None:
        return _encode_none()
    elif isinstance(x, str):
        return _encode_str(x)
    elif isinstance(x, int):
        return _encode_int(x)
    elif isinstance(x, bool):
        return _encode_bool(x)
    else:
        raise ValueError("Can't encode {0}", repr(x))


def _decode_data(data):
    buf = StringIO.StringIO(data)
    values = []
    while True:
        code = buf.read(1)
        if code == '':
            break
        code = struct.unpack('!B', code)[0]

        if code == TYPE_NONE:
            value = None
        elif code == TYPE_STR:
            value = _decode_str(buf)
        elif code == TYPE_INT:
            value = _decode_int(buf)
        elif code == TYPE_BOOL:
            value = _decode_bool(buf)
        else:
            raise ValueError("Invalid opcode: {0}".format(code))

        values.append(value)

    # Convert [(a, b), (c, d), ...] to {a: b, c: d, ...}
    values_iter = iter(values)
    return dict((key, value) for key, value in zip(values_iter, values_iter))


def _decode_str(buf):
    strlen = struct.unpack('!H', buf.read(2))[0]
    return buf.read(strlen)


def _decode_int(buf):
    return struct.unpack('!i', buf.read(4))[0]


def _decode_bool(buf):
    return struct.unpack('!B', buf.read(1))[0] == 1


def test_encode_decode():
    secret_key = b'foobar'
    initial = {'foo': 42, 'bar': True, 1337: None}
    encoded = encode_parameters(secret_key, initial)
    decoded = decode_parameters(secret_key, encoded)
    assert decoded == initial


if __name__ == '__main__':
    test_encode_decode()
