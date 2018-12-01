#!/usr/bin/env python2.7
import os
import sys
import json
import random
import string
from Crypto.PublicKey import RSA

# This service provides digital signatures!

################ RSA CREDENTIALS ################
N = None
P = None
Q = None
PHI = None
E = 65537
D = None

FILE_DIR = 'files'

def service():
    print "Hi! Welcome to our note storage system. It's based on RSA!"
    print "What do you want to do?"
    print "1. Write a Note -> Type W"
    print "2. Reading a specific note? -> Type R"
    print "3. Request for a signature of your integer? -> Type S"
    sys.stdout.flush()

    cmd = raw_input()
    if cmd == "W":
        write_note()
    elif cmd == "R":
        read_note()
    elif cmd == "S":
        sign()

def generate_random_note_id():
    return '1111' + ''.join(random.choice(string.digits) for x in range(36))

def sign():
    print "Here is our public key (you need them in order to verify the signature): N E"
    print N, E
    print "Please type: number!"
    print "We don't sign integers starting with for consecutive ones!"
    sys.stdout.flush()
    number = raw_input()
    if len(number) >= 3 and number[0:4] == '1111':
        print "We told you! we will not sign integers starting with for consecutive ones!"
        sys.stdout.flush()
    elif number.isdigit():
        s = dec(int(number))
        print "The signature: "
        print s
        sys.stdout.flush()
        return s
    else:
        print "Not a number!"
        sys.stdout.flush()

def read_note():
    print "Please type: note_id token"
    sys.stdout.flush()
    note_id, token = raw_input().split(' ', 2)

    # Files are named "<id>" and "<id>_password"
    try:
        with open("{}/{}".format(FILE_DIR, note_id)) as f:
            json_data = json.load(f)
            real_token = json_data['token']
            content = json_data['content']
    except Exception as e:
        print "wrong note_id!"
        sys.stdout.flush()
        return

    if token != real_token:
        print "Wrong token!"
        sys.stdout.flush()
        return

    print "Note content: ", content
    sys.stdout.flush()

def write_note():
    while True:
        note_id = generate_random_note_id()
        if not os.path.isfile(note_id):
            break
    print "Please type: content (in just one line)"
    sys.stdout.flush()

    content = raw_input()

    token = str(dec(int(note_id)))

    with open("{}/{}".format(FILE_DIR, note_id), "wx") as f:
        json.dump({'token': token, 'content': content}, f)
    print "Your note is safe with us! You can retrieve it later by these information: note_id token"
    print note_id, token
    sys.stdout.flush()

###################################### RSA Requirements ######################################

def enc(x):
    return modpow(x, E, N)

def dec(c):
    return modpow(c, D, N)

def modpow(a, b, m):
    result = 1
    a = a % m
    while b > 0:
        if b % 2 == 0:
            a = a * a % m
            b = b / 2
        else:
            result = (result * a) % m
            b = b - 1
    return result

def initialize_rsa_credentials():
    global N, P, Q, PHI, E, D
    if os.path.isfile('rsa.txt'):
        with open('rsa.txt') as rsa_data:
            rsa_credentials = json.load(rsa_data)
            N = rsa_credentials['N']
            P = rsa_credentials['P']
            Q = rsa_credentials['Q']
            PHI = rsa_credentials['PHI']
            E = rsa_credentials['E']
            D = rsa_credentials['D']
            return

    key = RSA.generate(1024, e=E)
    N = getattr(key.key, 'n')
    P = getattr(key.key, 'p')
    Q = getattr(key.key, 'q')
    D = getattr(key.key, 'd')
    PHI = (P - 1) * (Q - 1)

    with open('rsa.txt', 'w') as file:
        json.dump({'N': N, 'P': P, 'Q': Q, 'E': E, 'D': D, 'PHI': PHI}, file)

###################################### RSA Requirements ######################################

def make_file_dir():
    if not os.path.isdir(FILE_DIR):
        os.makedirs(FILE_DIR)

if __name__ == "__main__":
    initialize_rsa_credentials()
    make_file_dir()
    service()
