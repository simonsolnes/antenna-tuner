#!C:/Users/Sander/AppData/Local/Microsoft/WindowsApps/PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0/python.exe
import tkinter as tk
from tkinter import StringVar, messagebox
from tkinter.constants import W
import json
import time
import sys
if sys.platform != 'darwin':
    from relay_board import RelayArray, NO, NC, DeviceNotConnected
else:
    from relay_board_dummy import RelayArray, NO, NC, DeviceNotConnected

def from_rgb(rgb):
    return "#%02x%02x%02x" % rgb

constants = {
    'red': from_rgb((220, 100, 100)),
    'green': from_rgb((60, 180, 60)),
    'user_settings_path': 'user_settings.json' if sys.platform == 'darwin' else '/Users/Sander/Documents/Simon/antenna-tuner/user_settings.json'
}

labels = []
toggle_buttons = []
nc_buttons = []
no_buttons = []

class UserSettings(dict):
    def __init__(self):
        self.load()
    def load(self):
        with open(constants['user_settings_path'], 'r') as f:
            for k, v in json.loads(f.read()).items():
                self[k] = v
    def write(self):
        with open(constants['user_settings_path'], 'w') as f:
            f.write(json.dumps(self))

def make_user_connect():
    while not relays.is_connected:
        try:
            relays.connect()
        except DeviceNotConnected:
            result = tk.messagebox.askretrycancel(title='Connection Error', message='USB Relay not connected', detail='Try to replug')
            if not result:
                exit()

def update_status():
    def set_button_active(button):
        if sys.platform != 'darwin':
            button.config(bg=constants['red'])
        else:
            button.config(fg=constants['red'])
    def set_button_inactive(button):
        if sys.platform != 'darwin':
            button.config(bg=constants['button_color'])
        else:
            button.config(fg=from_rgb((255, 255, 255)))
    make_user_connect()
    for state, nc_button, no_button in zip(relays.status, nc_buttons, no_buttons):
        if state:
            set_button_active(no_button)
            set_button_inactive(nc_button)
        else:
            set_button_inactive(no_button)
            set_button_active(nc_button)

def update_settings():
    for attrs, label, nc_b, no_b in zip(UserSettings().values(), labels, nc_buttons, no_buttons): 
        label.config(text=attrs['label'])
        nc_b['text'] = attrs['nc']
        no_b['text'] = attrs['no']

def settings():
    label_config = tk.Toplevel(root)
    label_config.title("Configure Labels")

    label_config_table = tk.Frame(label_config)
    label_config_table.pack()

    user_settings = UserSettings()

    label_vars = [StringVar(value=user_settings[str(i+1)]['label']) for i in range(8)]
    nc_vars = [StringVar(value=user_settings[str(i+1)]['nc']) for i in range(8)]
    no_vars = [StringVar(value=user_settings[str(i+1)]['no']) for i in range(8)]

    tk.Label(label_config_table, text='Relay Label').grid(row=0, column=1)
    tk.Label(label_config_table, text='NC Label').grid(row=0, column=2)
    tk.Label(label_config_table, text='NO Label').grid(row=0, column=3)
    for i in range(8):
        tk.Label(label_config_table, text='Relay {}'.format(i + 1)).grid(row=i+1, column=0)
        tk.Entry(label_config_table, textvariable=label_vars[i], width=30).grid(row=i+1, column=1)
        tk.Entry(label_config_table, textvariable=nc_vars[i], width=20).grid(row=i+1, column=2)
        tk.Entry(label_config_table, textvariable=no_vars[i], width=20).grid(row=i+1, column=3)
    
    def cancel():
        pass

    def save():
        for i, (lbl, nc, no) in enumerate(zip(label_vars, nc_vars, no_vars)):
            user_settings[str(i+1)]['label'] = lbl.get()
            user_settings[str(i+1)]['nc'] = nc.get()
            user_settings[str(i+1)]['no'] = no.get()
        user_settings.write()
        update_settings()

    cancel_save = tk.Frame(label_config, pady=20)
    cancel_save.pack()
    tk.Button(cancel_save, text='Cancel', command=cancel).grid(row=0, column=0)
    tk.Button(cancel_save, text='Save', command=save).grid(row=0, column=1)

def create_toggle(relay_number):
    def toggle():
        make_user_connect()
        relays.toggle(relay_number)
        update_status()
    return toggle

def create_setter(relay_number, state):
    def set():
        make_user_connect()
        relays.set(relay_number, state)
        update_status()
    return set

root = tk.Tk()
root.title("Relay Array")
relay_table = tk.Frame(root, padx=10, pady=10)
relay_table.pack()

tk.Label(relay_table, text='Relay').grid(row=0, column=0, padx=4, pady=4)
settings_button = tk.Button(relay_table, text="Settings", command=settings)
settings_button.grid(row=0, column=1)
constants['button_color'] = settings_button.cget("background")
tk.Label(relay_table, text='NC').grid(row=0, column=3, padx=4, pady=4)
tk.Label(relay_table, text='NO').grid(row=0, column=4, padx=4, pady=4)

user_settings = UserSettings()

for relay_num, row in zip(range(1, 9), range(1, 9)):
    # 0 Relay title
    tk.Label(relay_table, text=str(relay_num)).grid(row=row, column=0, padx=4, pady=4)

    # 1 Label
    label = tk.Label(relay_table, text=user_settings[str(relay_num)]['label'])
    label.grid(row=row, column=1, padx=4, pady=4, sticky='w')
    labels.append(label)

    # 2 Toggle
    toggle_button = tk.Button(relay_table, text="Toggle", bg=from_rgb((230, 230, 230)), command=create_toggle(relay_num))
    toggle_button.grid(row=row, column=2, padx=4, pady=4)
    toggle_buttons.append(toggle_button)

    # 3 NC
    nc_button = tk.Button(relay_table, text=user_settings[str(relay_num)]['nc'], command=create_setter(relay_num, NC))
    nc_button.grid(row=row, column=3, padx=4, pady=4)
    nc_buttons.append(nc_button)

    # 4 NO
    no_button = tk.Button(relay_table, text=user_settings[str(relay_num)]['no'], command=create_setter(relay_num, NO))
    no_button.grid(row=row, column=4, padx=4, pady=4)
    no_buttons.append(no_button)

relays = RelayArray()
update_status()
'''
def openColorDialog():
    # display color dialog box
    color = colorDialog.show()
    # show the chosen RBG value
    tkinter.messagebox.showinfo("Notice", "The color you chose is: " + color[1] + "n" + 
        "R = " + str(color[0][0]) + " G = " + str(color[0][1]) + " B = " + str(color[0][2]))
colorDialog = tkinter.colorchooser.Chooser(root)
tk.Button(root, text='color', command=openColorDialog).pack()
'''
root.mainloop()