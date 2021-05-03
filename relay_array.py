#!/usr/bin/env python3
import hid
from time import sleep

class DeviceNotConnected(Exception):
    pass

on = True
off = False

NO = True
NC = False

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
        self.vid = vid
        self.pid = pid
        self.verbose = verbose

    def connect(self):
        try:
            self.h = hid.Device(self.vid, self.pid)
        except hid.HIDException as e:
            if str(e) == 'unable to open device':
                raise DeviceNotConnected()
            else:
                raise e

    def close(self):
        self.h.close()

    @property
    def is_connected(self):
        if not hasattr(self, 'h'):
            return False
        try:
            self.status
            return True
        except DeviceNotConnected:
            return False

    def __repr__(self):
        return 'RELAY: ' + ', '.join([str(idx) + ': ' + ('ON' if val else 'OFF') for idx, val in enumerate(self.status)])


    @property
    def status(self):
        try:
            switch_statuses = self.h.get_feature_report(1, 8)[7]
        except hid.HIDException:
            raise DeviceNotConnected()
        return [bool(int(x)) for x in list('{0:08b}'.format(switch_statuses))][::-1]

    def _send(self, *message):
        msg = bytes(message)
        try:
            self.h.send_feature_report(msg)
        except hid.HIDException:
            raise DeviceNotConnected()

    def get(self, relay_number):
        assert relay_number >= 1
        assert relay_number <= 8
        return self.status[relay_number - 1]

    def set(self, relay_number, state):
        assert relay_number >= 1
        assert relay_number <= 8
        assert isinstance(state, bool)
        self._send(constants['single_on' if state else 'single_off'], relay_number)

    def toggle(self, relay_number):
        if self.get(relay_number):
            self.set(relay_number, off)
        else:
            self.set(relay_number, on)

    def all_on(self):
        self._send(constants['all_on'])

    def all_off(self):
        self._send(constants['all_off'])

    def test_run(self):
        self.all_on()
        sleep(0.3)
        self.all_off()
        sleep(0.3)
        for i in range(1, 9):
            self.set(i, on)
            sleep(0.05)
        sleep(0.3)
        for i in range(1, 9)[::-1]:
            self.set(i, off)
            sleep(0.05)
        sleep(0.3)
        for t in [0.05, 0.01, 0.005]:
            for i in range(1, 9):
                for s in [on, off]:
                    self.set(i, s)
                    sleep(t)
            sleep(0.3)

