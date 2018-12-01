import json
import os
import random
import sys

from api import decode_parameters
from firmware import upload_firmware
from utils import clear_screen, read_prompt, hit_enter, unbase32, hashify, read_secret


RAMSTEIN_LOGO = """
  ____                     _       _       
 |  _ \ __ _ _ __ ___  ___| |_ ___(_)_ __  
 | |_) / _` | '_ ` _ \/ __| __/ _ \ | '_ \ 
 |  _ < (_| | | | | | \__ \ ||  __/ | | | |
 |_| \_\__,_|_| |_| |_|___/\__\___|_|_| |_|

 Drone Operation Center, Germany.

"""[1:]

RAMSTEIN_SCREEN = """
You are now in Ramstein. What do you want do?
1. Execute order
2. Upload firmware to drone
3. Leave Ramstein
""".lstrip()

FIRMWARE_SCREEN = """
Please provide a valid firmware for the drone. Must be base64 encoded.
""".lstrip()

EXECUTE_ORDER_SCREEN = """
Please give me a signed order.
""".lstrip()

GETRESULTS_SCREEN = """
Action: {operation}
Terrorist: {terrorist}
Notes: {notes}

Result: {message}

""".lstrip()

KILL_MESSAGES = [
    'Ooops. That was a marriage party. We killed many civilians.',
    'Oh, it was a Pakistani child. Now the ground is red, how funny!',
    'Sentenced to death. Without trial. Nation of law!',
    'Ohh, that guys around the fuel tanker were civilians? Thanks Mr. Klein!',
    'The terrorists\' son celebrated his birthday. We killed a lot of future terrorists. A good day for America.',
    'One shot missed and hit a building of Doctors Without Borders. Surely they also treated terrorists.',
    'It seems they stored explosives there, we destroyed the whole block. Nice firework though.',
    'He was hiding in a hospital but we got him. They had it coming for helping terrorists.',
    'That wasn\'t a rocket launcher? It definitely looked dangerous.',
    'Mission successful and just a little collateral damage.'
]

TRACE_MESSAGES = [
    'We saw some bearded old man.',
    'A guy with a large rifle. That is OUR rifle, how did he get it?'
]

class Ramstein:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.secret_key = read_secret(os.path.join(base_dir, 'rw', 'config', 'ramstein.ini'))

    def run(self):
        while True:
            clear_screen()
            sys.stdout.write(RAMSTEIN_LOGO)
            sys.stdout.write(RAMSTEIN_SCREEN)
            no = read_prompt()
            clear_screen()
            if no == '1':
                self._execute_order()
            elif no == '2':
                self._upload_firmware()
            elif no == '3':
                break

    def _execute_order(self):
        """ Execute an order. The order must be signed by Creech supervisor."""
        sys.stdout.write(RAMSTEIN_LOGO)
        sys.stdout.write(EXECUTE_ORDER_SCREEN)
        signed_order = read_prompt()
        try:
            order = decode_parameters(self.secret_key, unbase32(signed_order))
        except ValueError:
            sys.stdout.write('Invalid order.\n')
            hit_enter()
            return

        operation = self._load_operation(order.get('terrorist'))
        if operation is None:
            sys.exit(1)
        if order.get('operation') == 'getresult':
            # The soldier has to execute an operation first before asking
            # for results
            if not operation.get('executed', False):
                sys.stdout.write('This operation was not yet executed.\n')
                hit_enter()
                return

            # The operation was executed, we either killed or traced or killed
            # somebody. Show the result.
            if operation.get('operation') == 'kill':
                message = random.choice(KILL_MESSAGES)
            else:
                message = random.choice(TRACE_MESSAGES)
            sys.stdout.write(GETRESULTS_SCREEN.format(
                operation=operation.get('operation', ''),
                terrorist=operation.get('terrorist', ''),
                notes=operation.get('notes', ''),
                message=message
            ))
            hit_enter()
            return
        else:
            # This is either a kill or trace operation, mark it as executed.
            operation['executed'] = True
            self._store_operation(operation)
            sys.stdout.write('Operation will be executed, come back for results.\n')
            hit_enter()
            return

    def _upload_firmware(self):
        """ Upload new firmware to the drone.

        The firmware must be valid Python bytecode with some restrictions.
        See firmware.py for details.
        """
        sys.stdout.write(RAMSTEIN_LOGO)
        sys.stdout.write(FIRMWARE_SCREEN)
        firmware = read_prompt()
        outdir = os.path.join(self.base_dir, 'rw')
        if upload_firmware(outdir, firmware):
            sys.stdout.write('Uploaded firmware.\n')
        else:
            sys.stdout.write('Invalid firmware.\n')
        hit_enter()

    #
    # Utility functions
    #

    def _load_operation(self, terrorist):
        filename = self._get_operation_filename(terrorist)
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except IOError:
            return None

    def _store_operation(self, operation_data):
        filename = self._get_operation_filename(operation_data['terrorist'])
        with open(filename, 'w') as f:
            json.dump(operation_data, f)

    def _get_operation_filename(self, terrorist):
        return os.path.join(self.base_dir, 'rw', 'operations',
                            hashify(self.secret_key, terrorist) + '.json')
