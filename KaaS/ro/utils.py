import base64
import ConfigParser
import fcntl
import hashlib
import hmac
import os
import random
import sys


def clear_screen():
    sys.stdout.write('\033[2J\033[1;1H')
    sys.stdout.flush()


def read_prompt():
    sys.stdout.write('\033[35;1m')
    sys.stdout.write('> ')
    sys.stdout.flush()
    line = sys.stdin.readline()
    sys.stdout.write('\033[0m')
    if not line:
        sys.exit(1)
    if len(line) > 1024:
        sys.exit(1)
    return line.strip()


def hit_enter():
    sys.stdout.write('\033[35;1m')
    sys.stdout.write('\n[hit enter to continue]\n> ')
    sys.stdout.flush()
    sys.stdin.readline()
    sys.stdout.write('\033[0m')


def hashify(secret_key, message):
    return hmac.new(secret_key, message, hashlib.sha256).hexdigest()


def base32(x):
    x = base64.b32encode(x)
    num_pad = x.count('=')
    if num_pad == 0:
        return x
    extra = ''.join(random.choice(('0', '1')) for _i in xrange(num_pad))
    return x[:-num_pad] + extra


def unbase32(x):
    try:
        return base64.b32decode(x.replace('0', '=').replace('1', '='))
    except TypeError:
        raise ValueError('unbase32 error')


def read_secret(filename):
    p = ConfigParser.ConfigParser()
    p.read([filename])
    return p.get('secrets', 'secret_key').strip()



ramstein_config = """
[general]
required_deaths_per_day = 17
enable_firmware_upload = yes

[secrets]
; Must match with all other U.S. military institutions
; If you have to change it, change it on every institution
secret_key = {key}
""".lstrip()

creech_config = """
[general]
permit_kill_order = yes
take_responsibility = no

[secrets]
; Must match with all other U.S. military institutions
; If you have to change it, change it on every institution
secret_key = {key}
""".lstrip()


def generate_keys(config_dir):
    """Generate new cryptographic keys.

    Is executed on the first run of the service.
    """
    ramstein_ini = os.path.join(config_dir, 'ramstein.ini')
    creech_ini = os.path.join(config_dir, 'creech.ini')
    lock_file = os.path.join(config_dir, '.lock')
    if not os.path.exists(ramstein_ini) or not os.path.exists(creech_ini):
        with open(lock_file, 'w') as f_lock:
            try:
                fcntl.lockf(f_lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                return
            try:
                key = base64.b32encode(os.urandom(15))
                with open(ramstein_ini, 'w') as f:
                    f.write(ramstein_config.format(key=key))
                with open(creech_ini, 'w') as f:
                    f.write(creech_config.format(key=key))
            finally:
                fcntl.lockf(f_lock.fileno(), fcntl.LOCK_UN)
