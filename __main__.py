#!C:/Users/Sander/AppData/Local/Microsoft/WindowsApps/PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0/python.exe
import tkinter as tk
from tkinter import StringVar, messagebox
from tkinter.constants import W
from relay_board import RelayArray, NO, NC, DeviceNotConnected
import json
import time

def from_rgb(rgb):
    return "#%02x%02x%02x" % rgb
constants = {
    'user_labels_path': '/Users/Sander/Documents/Simon/antenna-tuner/user_labels.json',
    'bg_color': from_rgb((220, 100, 100)),
    'green': from_rgb((60, 180, 60))
}

# TODO: same button width

root = tk.Tk()
root.title("Relay Array")

relays = RelayArray()

def make_user_connect():
    while not relays.is_connected:
        try:
            relays.connect()
        except DeviceNotConnected:
            result = tk.messagebox.askretrycancel(title='Connection Error', message='USB Relay not connected', detail='Try to replug')
            if not result:
                exit()
make_user_connect()


labels = []
nc_buttons = []
no_buttons = []
activate_buttons = []


def update_status():
    make_user_connect()
    for state, nc_button, no_button in zip(relays.status, nc_buttons, no_buttons):
        if state:
            nc_button.config(bg=constants['button_color'])
            no_button.config(bg=constants['bg_color'])
        else:
            nc_button.config(bg=constants['bg_color'])
            no_button.config(bg=constants['button_color'])

def read_user_labels():
    with open(constants['user_labels_path'], 'r') as f:
        return json.loads(f.read())

def write_user_labels(inp):
    with open(constants['user_labels_path'], 'w') as f:
        return f.write(json.dumps(inp))

def update_labels():
    for attrs, label, nc_b, no_b, a_b in zip(read_user_labels().values(), labels, nc_buttons, no_buttons, activate_buttons): 
        label.config(text=attrs['label'])
        nc_b['text'] = attrs['nc']
        no_b['text'] = attrs['no']
        a_b['text'] = attrs['activation_time']

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
def create_activator(relay_number):
    def activate():
        at = read_user_labels()[str(relay_number)]['activation_time']
        try:
            at = float(at)
        except ValueError:
            tk.messagebox.showerror(message='activation time has be a number, decimal seperator: .')
            return

        relays.toggle(relay_number)
        update_status()
        time.sleep(at)
        relays.toggle(relay_number)
        update_status()
    return activate

def rap(func):
    def inside():
        make_user_connect()
        func()
        update_status()
    return inside

def configure_labels():
    label_config = tk.Toplevel(root)
    label_config.title("Configure Labels")

    label_config_table = tk.Frame(label_config)
    label_config_table.pack()

    current = read_user_labels()

    label_vars = [StringVar(value=current[str(i+1)]['label']) for i in range(8)]
    nc_vars = [StringVar(value=current[str(i+1)]['nc']) for i in range(8)]
    no_vars = [StringVar(value=current[str(i+1)]['no']) for i in range(8)]
    activation_time_vars = [StringVar(value=current[str(i+1)]['activation_time']) for i in range(8)]

    tk.Label(label_config_table, text='Relay Label').grid(row=0, column=1)
    tk.Label(label_config_table, text='NC Label').grid(row=0, column=2)
    tk.Label(label_config_table, text='NO Label').grid(row=0, column=3)
    tk.Label(label_config_table, text='Activation time (s)').grid(row=0, column=4)
    for i in range(8):
        tk.Label(label_config_table, text='Relay {}'.format(i + 1)).grid(row=i+1, column=0)
        tk.Entry(label_config_table, textvariable=label_vars[i], width=30).grid(row=i+1, column=1)
        tk.Entry(label_config_table, textvariable=nc_vars[i], width=30).grid(row=i+1, column=2)
        tk.Entry(label_config_table, textvariable=no_vars[i], width=30).grid(row=i+1, column=3)
        tk.Entry(label_config_table, textvariable=activation_time_vars[i], width=30).grid(row=i+1, column=4)
    
    def cancel():
        pass
    def save():
        new = {i: {} for i in range(1, 9)}
        for i, (lbl, nc, no, at) in enumerate(zip(*[[x.get() for x in l] for l in [label_vars, nc_vars, no_vars, activation_time_vars]])):
            new[i+1] = {'label': lbl, 'nc': nc, 'no': no, 'activation_time': at}
        write_user_labels(new)
        update_labels()

    cancel_save = tk.Frame(label_config, pady=20)
    cancel_save.pack()
    tk.Button(cancel_save, text='Cancel', command=cancel).grid(row=0, column=0)
    tk.Button(cancel_save, text='Save', command=save).grid(row=0, column=1)




relay_table = tk.Frame(root, padx=10, pady=10)
relay_table.pack()


tk.Label(relay_table, text='Relay').grid(row=0, column=0, padx=4, pady=4)
configure_labels_button = tk.Button(relay_table, text="Configure Labels", command=configure_labels)
configure_labels_button.grid(row=0, column=1)
tk.Label(relay_table, text='Time').grid(row=0, column=3, padx=4, pady=4)
tk.Label(relay_table, text='NC').grid(row=0, column=4, padx=4, pady=4)
tk.Label(relay_table, text='NO').grid(row=0, column=5, padx=4, pady=4)

constants['button_color'] = configure_labels_button.cget("background")

for relay_num, row in zip(range(1, 9), range(1, 9)):
    # 0 Relay title
    tk.Label(relay_table, text=str(relay_num)).grid(row=row, column=0, padx=4, pady=4)

    # 1 Label
    label = tk.Label(relay_table, text='User Label')
    labels.append(label)
    label.grid(row=row, column=1, padx=4, pady=4, sticky='w')

    # 2 Toggle
    tk.Button(relay_table, text="Toggle", bg=from_rgb((230, 230, 230)), command=create_toggle(relay_num)).grid(row=row, column=2, padx=4, pady=4)

    # 3 Activate
    a_button = tk.Button(relay_table, command=create_activator(relay_num), bg=constants['green'])
    activate_buttons.append(a_button)
    a_button.grid(row=row, column=3, padx=4, pady=4)

    # 4 NC
    nc_button = tk.Button(relay_table, command=create_setter(relay_num, NC))
    nc_buttons.append(nc_button)
    nc_button.grid(row=row, column=4, padx=4, pady=4)

    # 5 NO
    no_button = tk.Button(relay_table, command=create_setter(relay_num, NO))
    no_buttons.append(no_button)
    no_button.grid(row=row, column=5, padx=4, pady=4)




update_status()
update_labels()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

win_size = tuple(int(_) for _ in root.geometry().split('+')[0].split('x'))

x = screen_width/2 - 500
y = screen_height/4 - win_size[1]/2

root.geometry("+%d+%d" % (x, y))


root.mainloop()


