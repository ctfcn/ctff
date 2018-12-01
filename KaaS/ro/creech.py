import json
import os
import re
import stat
import sys

from api import encode_parameters, decode_parameters
from utils import clear_screen, read_prompt, hit_enter, hashify, base32, read_secret


CREECH_LOGO = """
   ____                    _     
  / ___|_ __ ___  ___  ___| |__  
 | |   | '__/ _ \/ _ \/ __| '_ \ 
 | |___| | |  __/  __/ (__| | | |
  \____|_|  \___|\___|\___|_| |_|

  U.S. Air Force Base, Nevada, USA.
                                 
"""[1:]

MAIN_SCREEN = """
Welcome soldier!

1. Get permission for drone operation
2. Leave Creech
""".lstrip()

PERMISSION_SCREEN = """
Choose drone operation (trace, kill, peace):
""".lstrip()


NAME_RE = re.compile('^[a-zA-Z]+ [a-zA-Z]+$')


class Creech:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.secret_key = read_secret(os.path.join(base_dir, 'rw', 'config', 'creech.ini'))

    def run(self):
        while True:
            clear_screen()
            if not self._main_screen():
                break


    def _main_screen(self):
        """Main screen. This is what you get when you visit Creech. """
        sys.stdout.write(CREECH_LOGO)
        sys.stdout.write(MAIN_SCREEN)
        no = read_prompt()
        if no == '1':
            self._get_permission()
        elif no == '2':
            return False
        return True


    def _get_permission(self):
        """Ask the soldier for details about his planned operation.

        The soldiers asks for permission to execute a specific drone operation.
        He can choose if he want to trace or kill the terrorist. If HIS drone
        operation was already executed he can also ask for the results of the
        operation.

        The supervisor will give a signed order if he permits the operation.
        This order can be given to Ramstein to execute the operation.

        Since we are in the war of terror permission is likely to be given.
        """
        clear_screen()
        sys.stdout.write(CREECH_LOGO)
        sys.stdout.write(PERMISSION_SCREEN)
        operation = read_prompt()
        if operation not in ('trace', 'kill', 'peace'):
            sys.stdout.write('Are you too stupid? Army has seen better soldiers than you!\n')
            self._dismiss()
            return
        if operation == 'peace':
            sys.stdout.write('This is WAR on terror, not peace on terror!\n')
            sys.stdout.write('We have to creat^W kill more terrorists.\n')
            self._dismiss()
            return
        elif operation in ('trace', 'kill'):
            if operation == 'trace':
                sys.stdout.write('Which terrorist should be traced?\n')
            elif operation == 'kill':
                sys.stdout.write('Which terrorist should be killed?\n')
            terrorist = read_prompt()
            if terrorist.lower() == 'obama':
                sys.stdout.write('Did you mean Osama? [yes/no]\n')
                if read_prompt().lower() != 'yes':
                    sys.stdout.write('Idiot! This is our president.\n')
                    sys.stdout.write('[mumbles to himself: He might be a terrorist too]\n')
                    self._dismiss()
                    return
                else:
                    sys.stdout.write('He was already murdered, but I guess there are more Osamas.\n')
                sys.stdout.write('\n')
            if os.path.exists(self._get_operation_filename(terrorist)):
                sys.stdout.write('There is already an ongoing operation against {}.\n'.format(terrorist))
                sys.stdout.write('Anyway, thank you helping us in our war on terror.\n')
                hit_enter()
                return


            sys.stdout.write('Secret notes regarding this target?\n')
            notes = read_prompt()

            operation_data = {
                'operation': operation,
                'terrorist': terrorist,
                'notes': notes
            }
            self._store_operation(operation_data)
            self._grant_permission(operation, terrorist)

    def _grant_permission(self, operation, terrorist):
        """Grants permission to an operation.

        The soldiers gets a signed order which can be passed to Ramstein to
        execute the drone operation.
        """
        order = base32(encode_parameters(self.secret_key, {
            'operation': operation,
            'terrorist': terrorist
        }))
        order_getresult = base32(encode_parameters(self.secret_key, {
            'operation': 'getresult',
            'terrorist': terrorist
        }))

        sys.stdout.write('\nPermission granted!\n\n')
        sys.stdout.write('{} order: '.format(operation))
        sys.stdout.write(order)
        sys.stdout.write('\ngetresult order: ')
        sys.stdout.write(order_getresult)
        sys.stdout.write('\n\nYou can use these signed orders in Ramstein!\n')
        sys.stdout.write('The first order can be used to execute the drone operation.\n')
        sys.stdout.write('The second order can be used to retrieve the results.\n')
        hit_enter()

    def _dismiss(self):
        """ The soldier misbehaved. Either return him or kill his connection. """
        sys.stdout.write('Dismiss!\n')
        sys.stdout.write(' [colleague whispers to you: Say "Affirmative!"]\n')
        if read_prompt().lower() != 'affirmative!':
            sys.exit(1)

    #
    # Utility functions
    #

    def _store_operation(self, operation_data):
        filename = self._get_operation_filename(operation_data['terrorist'])
        with open(filename, 'w') as f:
            os.fchmod(f.fileno(),  stat.S_IRUSR | stat.S_IWUSR)
            json.dump(operation_data, f)

    def _load_operation(self, terrorist):
        filename = self._get_operation_filename(terrorist)
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except IOError:
            return None

    def _get_operation_filename(self, terrorist):
        return os.path.join(self.base_dir, 'rw', 'operations',
                            hashify(self.secret_key, terrorist) + '.json')
