#!/usr/bin/env python3
from tkinter.constants import W
import hid
from time import sleep

on = True
off = False

constants = {
    'vid': 0x16c0,
    'pid': 0x05df,
    'all_on': 0xFE,
    'all_off': 0xFC,
    'single_on': 0xFF,
    'single_off': 0xFD
}

class RelayArray:
    def __init__(self, vid=0x16c0, pid=0x05df, verbose = True):
        try:
            self.h = hid.Device(vid, pid)
        except hid.HIDException as e:
            print('There was an error:', e)
            exit()

    def __repr__(self):
        return 'RELAY: ' + ', '.join([str(idx) + ': ' + ('ON' if val else 'OFF') for idx, val in enumerate(self.status)])
    def close(self):
        self.h.close()

    @property
    def status(self):
        switch_statuses = self.h.get_feature_report(1, 8)[7]
        return [bool(int(x)) for x in list('{0:08b}'.format(switch_statuses))][::-1]
    
    def send(self, *message):
        msg = bytes(message)
        self.h.send_feature_report(msg)
    
    def __getitem__(self, relay_number):
        assert relay_number >= 1
        assert relay_number <= 8
        return self.status[relay_number - 1]
    
    def __setitem__(self, relay_number, state):
        assert relay_number >= 1
        assert relay_number <= 8
        assert isinstance(state, bool)
        print('RA: setting relay', relay_number, 'with state:', 'ON' if state else 'OFF')
        self.send(constants['single_on' if state else 'single_off'], relay_number)
        
    def all_on(self):
        print('RA: setting all on')
        self.send(constants['all_on'])

    def all_off(self):
        print('RA: setting all off')
        self.send(constants['all_off'])
    
    def test_run(self):
        t = 0.1
        print("All on")
        self.all_on()
        print("All off")
        self.all_off()
        t = 0.1
        for i in range(1, 9):
            self[i] = on
        sleep(t)
        for i in range(1, 9):
            self[i] = off
def test_run():
    r = RelayArray()
    r.all_on()
    sleep(1)
    r.all_off()
    sleep(1)

    for i in range(1, 9):
        r[i] = on
        sleep(0.05)
    sleep(1)

    for i in range(1, 9)[::-1]:
        r[i] = off
        sleep(0.05)

    sleep(1)

    for i in range(1, 9):
        r[i] = on
        sleep(0.05)
        r[i] = off
        sleep(0.05)

    sleep(1)

    for i in range(1, 9):
        r[i] = on
        sleep(0.01)
        r[i] = off
        sleep(0.01)

    sleep(1)
    for i in range(5):
        for i in range(1, 9):
            r[i] = on
            sleep(0.006)
            r[i] = off
            sleep(0.006)
    r.close()

relays = RelayArray()
import tkinter
root = tkinter.Tk()
def create_setter(relay_number, state):
    def set():
        relays[relay_number] = state
    return set

for relay_num, row in zip(range(5, 9), range(0, 4)):
    tkinter.Button(root, text="{} ON".format(relay_num), command=create_setter(relay_num, on)).grid(row=row, column=0)
for relay_num, row in zip(range(5, 9), range(0, 4)):
    tkinter.Button(root, text="{} OFF".format(relay_num), command=create_setter(relay_num, off)).grid(row=row, column=1)

for relay_num, row in zip(range(1, 5)[::-1], range(0, 4)):
    tkinter.Button(root, text="{} ON".format(relay_num), command=create_setter(relay_num, on)).grid(row=row, column=2)
for relay_num, row in zip(range(1, 5)[::-1], range(0, 4)):
    tkinter.Button(root, text="{} OFF".format(relay_num), command=create_setter(relay_num, off)).grid(row=row, column=3)

    

root.mainloop()

