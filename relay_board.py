from dae_RelayBoard import dae_RelayBoard_Common
import dae_RelayBoard
class NO: pass
class NC: pass
class DeviceNotConnected(Exception): pass

class RelayArray():
    def __init__(self):
        pass

    def connect(self):
        try:
            self.dr = dae_RelayBoard.DAE_RelayBoard(dae_RelayBoard.DAE_RELAYBOARD_TYPE_8)
            self.dr.initialise()
        except dae_RelayBoard.dae_RelayBoard_Common.Denkovi_Exception as e:
            if hasattr(e, 'message') and e.message == 'FTD2XXWindows device not initialised':
                raise DeviceNotConnected

    @property
    def is_connected(self):
        if not hasattr(self, 'dr'):
            return False
        try:
            self.status
        except dae_RelayBoard.dae_RelayBoard_Common.Denkovi_Exception as e:
            return False
        return True

    @property
    def status(self):
        return list(self.dr.getStates().values())
    
    def set(self, relay_number, state):
        if state is NO:
            self.dr.setState(relay_number, True)
        elif state is NC:
            self.dr.setState(relay_number, False)
        else:
            raise Exception

    def toggle(self, relay_number):
        print("relay num", relay_number)
        print(self.status)
        if self.status[relay_number - 1]:
            self.set(relay_number, NC)
        else:
            self.set(relay_number, NO)
            
        
            
            