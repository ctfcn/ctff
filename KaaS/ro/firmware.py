import base64
import os
import subprocess


ALLOWED_OPS = [131, 28, 147, 65, 88, 83, 87, 120, 104, 1, 145, 122, 29, 141,
               77, 121, 90, 108, 116, 101, 93, 85, 91, 103, 107, 66, 57, 125,
               140, 146, 82, 119, 70, 98, 68, 0, 12, 62, 135, 84, 79, 24, 54,
               55, 75, 59, 95, 105, 143, 21, 76, 73, 92, 20, 74, 9, 94, 78,
               97, 56, 67, 5, 61, 64, 80, 132, 51, 50, 99, 142, 106, 27, 109,
               126, 23, 100, 137, 11, 10, 60, 102, 19, 89, 13, 22, 53, 52, 81,
               96, 115, 111, 71, 130, 30, 31, 32, 33, 114, 136, 124, 112, 26,
               63, 25, 86, 40, 41, 42, 43, 15, 72, 58, 133, 113, 134, 110]

HAVE_ARGUMENTS = 90

MAX_SIZE = 256


def verify_firmware(bytecode_str):
    n = len(bytecode_str)
    i = 0
    while i < n:
        c = bytecode_str[i]
        op = ord(c)
        if op not in ALLOWED_OPS:
            return False
        i += 1
        if op >= HAVE_ARGUMENTS:
            i += 2
    if i > MAX_SIZE:
        return False
    return True


def upload_firmware(outdir, firmware):
    try:
        bytecode_str = base64.b64decode(firmware)
    except (ValueError, TypeError):
        return False
    if not verify_firmware(bytecode_str):
        return False

    random_name = base64.b32encode(os.urandom(20))
    outfile = os.path.join(outdir, random_name + '.pyc')
    with open(outfile, 'wb') as f:
        f.write(bytecode_str)
    with open('/dev/null', 'w') as devnull:
        subprocess.call(['/usr/bin/python2.7', outfile],
                        stdout=devnull, stderr=devnull)
    os.remove(outfile)
    return True
