# encoding: utf-8
import base64
import os
import sys
import signal

from api import encode_parameters


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(BASE_DIR, 'ro'))


from utils import clear_screen, read_prompt, hit_enter
from ramstein import Ramstein
from creech import Creech

WELCOME_SCREEN = """

    ██ ▄█▀ ██▓ ██▓     ██▓     ██▓ ███▄    █   ▄████     
    ██▄█▒ ▓██▒▓██▒    ▓██▒    ▓██▒ ██ ▀█   █  ██▒ ▀█▒    
   ▓███▄░ ▒██▒▒██░    ▒██░    ▒██▒▓██  ▀█ ██▒▒██░▄▄▄░    
   ▓██ █▄ ░██░▒██░    ▒██░    ░██░▓██▒  ▐▌██▒░▓█  ██▓    
   ▒██▒ █▄░██░░██████▒░██████▒░██░▒██░   ▓██░░▒▓███▀▒    
   ▒ ▒▒ ▓▒░▓  ░ ▒░▓  ░░ ▒░▓  ░░▓  ░ ▒░   ▒ ▒  ░▒   ▒     
   ░ ░▒ ▒░ ▒ ░░ ░ ▒  ░░ ░ ▒  ░ ▒ ░░ ░░   ░ ▒░  ░   ░     
   ░ ░░ ░  ▒ ░  ░ ░     ░ ░    ▒ ░   ░   ░ ░ ░ ░   ░     
   ░  ░    ░      ░  ░    ░  ░ ░           ░       ░     
                                                         
          ▄▄▄        ██████        ▄▄▄                   
         ▒████▄    ▒██    ▒       ▒████▄                 
         ▒██  ▀█▄  ░ ▓██▄         ▒██  ▀█▄               
         ░██▄▄▄▄██   ▒   ██▒      ░██▄▄▄▄██              
          ▓█   ▓██▒▒██████▒▒       ▓█   ▓██▒             
          ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░       ▒▒   ▓▒█░             
           ▒   ▒▒ ░░ ░▒  ░ ░        ▒   ▒▒ ░             
           ░   ▒   ░  ░  ░          ░   ▒                
               ░  ░      ░              ░  ░             
                                                         
     ██████ ▓█████  ██▀███   ██▒   █▓ ██▓ ▄████▄  ▓█████ 
   ▒██    ▒ ▓█   ▀ ▓██ ▒ ██▒▓██░   █▒▓██▒▒██▀ ▀█  ▓█   ▀ 
   ░ ▓██▄   ▒███   ▓██ ░▄█ ▒ ▓██  █▒░▒██▒▒▓█    ▄ ▒███   
     ▒   ██▒▒▓█  ▄ ▒██▀▀█▄    ▒██ █░░░██░▒▓▓▄ ▄██▒▒▓█  ▄ 
   ▒██████▒▒░▒████▒░██▓ ▒██▒   ▒▀█░  ░██░▒ ▓███▀ ░░▒████▒
   ▒ ▒▓▒ ▒ ░░░ ▒░ ░░ ▒▓ ░▒▓░   ░ ▐░  ░▓  ░ ░▒ ▒  ░░░ ▒░ ░
   ░ ░▒  ░ ░ ░ ░  ░  ░▒ ░ ▒░   ░ ░░   ▒ ░  ░  ▒    ░ ░  ░
   ░  ░  ░     ░     ░░   ░      ░░   ▒ ░░           ░   
         ░     ░  ░   ░           ░   ░  ░ ░         ░  ░
                                 ░       ░               

 https://cinsects.de/killing-as-a-service

Where do you want to go today?
1. Drone Operation Center in Ramstein, Rhineland-Palatinate, Germany
2. Creech Air Force Base, Nevada, United States of America

Other operations:
3. Calibrate
4. Quit
"""[1:]


class KillingAsAService:
    def __init__(self):
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def run(self):
        while True:
            self._show_welcome()

    def _show_welcome(self):
        clear_screen()
        sys.stdout.write(WELCOME_SCREEN)
        no = read_prompt()
        if no == '1':
            self._show_ramstein()
        elif no == '2':
            self._show_headquarters()
        elif no == '3':
            self._calibrate()
        elif no == '4':
            sys.exit(0)

    def _show_ramstein(self):
        clear_screen()
        ramstein = Ramstein(BASE_DIR)
        ramstein.run()

    def _show_headquarters(self):
        clear_screen()
        hq = Creech(BASE_DIR)
        hq.run()

    def _calibrate(self):
        clear_screen()
        sys.stdout.write('Your calibration code?\n')
        code = read_prompt()
        sys.stdout.write('Here is your calibration data:\n')
        sys.stdout.write('{{{')
        sys.stdout.write(base64.b64encode(encode_parameters(code, {
            'calibration': code
        })))
        sys.stdout.write('}}}\n')
        hit_enter()

    def _handle_exit(self, signo, sigframe):
        try:
            sys.stdout.write('\033[0m\n\nBye!\n')
            sys.stdout.flush()
        except IOError:
            pass
        sys.exit(0)


kaas = KillingAsAService()
kaas.run()
