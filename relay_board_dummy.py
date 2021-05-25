class NO: pass
class NC: pass
class DeviceNotConnected(Exception): pass

class RelayArray():
    def __init__(self):
        self.state = [False for i in range(8)]

    def connect(self):
        pass

    @property
    def is_connected(self):
        return True

    @property
    def status(self):
        return self.state
    
    def set(self, relay_number, state):
        if state is NO:
            self.state[relay_number - 1] = True
        elif state is NC:
            self.state[relay_number - 1] = False
        else:
            raise Exception
        print(' '.join(['I' if x else 'O' for x in self.state]))

    def toggle(self, relay_number):
        if self.status[relay_number - 1]:
            self.set(relay_number, NC)
        else:
            self.set(relay_number, NO)
            
        
            
            