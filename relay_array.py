#!/usr/bin/env python3
from sys import platform
if platform == 'win32':
    import pywinusb.hid as winhid
elif platform == 'darwin':
    import hid
else:
    raise NotImplemented
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
        if platform == 'win32':
            self.connect_win()
        elif platform == 'darwin':
            self.connect_darwin()
        else:
            raise NotImplemented
        
    def connect_win(self):
        print('connecting')
        self.wh = winhid.HidDeviceFilter(vendor_id = self.vid).get_devices()[0]
        self.wh.open()
        print(type(self.wh))
        print('connected to', self.wh)

    def connect_darwin(self):
        try:
            self.h = hid.Device(self.vid, self.pid)
        except hid.HIDException as e:
            if str(e) == 'unable to open device':
                raise DeviceNotConnected()
            else:
                raise e

    def close(self):
        if platform == 'win32':
            raise NotImplemented
        elif platform == 'darwin':
            self.h.close()

    @property
    def is_connected(self):
        if platform == 'darwin' and not hasattr(self, 'h'):
            return False
        elif platform == 'win32' and not hasattr(self, 'wh'):
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
        if platform == 'darwin':
            return self.status_darwin()
        elif platform == 'win32':
            return self.status_win()
        else:
            raise NotImplemented
    def transpose_status(self, rawr):
        return [bool(int(x)) for x in list('{0:08b}'.format(rawr))][::-1]

    def status_win(self):
        report = self.wh.find_feature_reports()[0]
        r = report.get()
        print('status report:', r)
        return self.transpose_status(report.get_raw_data()[7])

        

    def status_darwin(self):
        try:
            switch_statuses = self.h.get_feature_report(1, 8)[7]
        except hid.HIDException:
            raise DeviceNotConnected()
        return self.transpose_status(switch_statuses)

    def _send(self, *message):
        msg = bytes(message)
        print('msg:', message, msg)
        if platform == 'darwin':
            try:
                self.h.send_feature_report(msg)
            except hid.HIDException:
                raise DeviceNotConnected()
        elif platform == 'win32':
            report = self.wh.find_feature_reports()[0]
            print('r', report)
            report[0] = constants['single_on']
            report.send()



    def get(self, relay_number):
        assert relay_number >= 1
        assert relay_number <= 8
        return self.status[relay_number - 1]

    def settt(self, relay_number, state):
        if platform == 'win32':
            self.set_win(relay_number, state)
        elif platform == 'darwin':
            self.set_darwin(relay_number, state)

    def set_win(self, relay_number, state):
        report = self.wh.find_feature_reports()[0]


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

