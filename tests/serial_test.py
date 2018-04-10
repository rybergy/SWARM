import time
import random
from threading import Thread
import serial

s = serial.Serial('COM3')  # change to relevant port


def echo():
    b = []
    while True:
        b.append(s.read())
        if b[-1].decode() == '\n':
            # trim opcode and \n
            message = b''.join(b[1:-1]).decode('unicode_escape')
            try:
                prefix = {
                    b'\0': 'ERROR',
                    b'\1': 'DEBUG',
                    b'\2': 'STATUS',
                    b'\3': 'GPS'
                }[b[0]]
                print(prefix + ': ' + message)
            except KeyError:
                print('KEYERROR')
            b = []
echo_thread = Thread(target=echo)


def change_state():
    while True:
        state: str = random.choice(['stop', 'forward', 'backward', 'left', 'right', 'auto'])
        print('STATE CHANGE: ' + state)
        s.write(state.encode())
        time.sleep(10)
state_thread = Thread(target=change_state)

echo_thread.start()
state_thread.start()
