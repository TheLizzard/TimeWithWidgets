from pathlib import Path
import tkinter as tk
import os.path

from .widget import Widget
from .notebook import partial


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = str(Path(BASE_DIR).parent)+"\\\\"

PADDING = '''
import importlib
import platform
import socket
import os

run = os.system


def require(module, function=None, functions=None):
    """
    Imports a module/functions from a module.
    Use like:
        print_function = require(module="builtins", function="print")
        str, int = require(module="builtins", functions=("str", "int"))
        builtins = require(module="builtins")
    Returns None if the module/function isn't found
    """
    assert (function is None) or (functions is None), "Require takes in 2 parameters"

    try:
        if function is None:
            if functions is None:
                return importlib.import_module(module)
            else:
                assert not isinstance(functions, str), "Functions should be a tuple/list"
                output = []
                for function in functions:
                    output.append(require(module=module, function=function))
                return output
        else:
            return importlib.import_module(module).__dict__[function]
    except:
        return None

def is_connected() -> bool:
    try:
        host = socket.gethostbyname("www.google.com")
        socket.create_connection((host, 80), 2).close()
        return True
    except Exception as error:
        return False

def is_64_bits() -> bool:
    return platform.machine().endswith("64")

def get_os_name() -> str:
    os = platform.system()
    return os.lower()
'''.strip().format(__file__=repr(__file__), BASE_DIR=repr(BASE_DIR))

COMMENTS = '''
# This is a comment
# This is has the python syntax
# It was some predefined variables like:
    {BASE_DIR}      # The base directory of the program
    {__file__}      # Gets the file currently running
# It was some predefined functions like:
    run(str)                  # Runs the str as a terminal command
    get_os_name() -> str      # returns the name of the OS
    is_64_bits() -> bool      # returns a true if the OS is 64 bits
    has_connection() -> bool  # Checks if there is internet connection
    change_dir(str)           # Changes the current directory
                              # Note: doesn't change the BASE_DIR variable

    require                   # Imports a module/functions from a module.
                              # Use like:
                              #     print_function = require(module="builtins", function="print")
                              #     str, int = require(module="builtins", functions=("str", "int"))
                              #     builtins = require(module="builtins")
                              # Returns None if the module/function isn't found
'''.strip()

DEFAULT_SCRIPT = '''
# Import some GUI components
showinfo = require(module="tkinter.messagebox", function="showinfo")
if showinfo is None:
    pass # tkinter isn't installed/setup
    exit()

# Get the user's computer username
getpass = require(module="getpass")
if getpass is None:
    showinfo("info", "No getpass module :-(")
    exit()

name = getpass.getuser()

# Show a box saying hi to the user
showinfo("info", "Hello %s!" % name)
'''.strip()


class RunnerWidget(Widget):
    def __init__(self, app):
        self.read()
        self.frame = tk.Frame(app.root)
        self.frame.grid(row=1, column=1)
        self.controls = tk.Frame(app.root)
        self.controls.grid(row=2, column=1)

        self.addbutton = tk.Button(self.controls, text="New", command=self.new)
        self.addbutton.grid(row=1, column=1, sticky="news")
        self.helpbutton = tk.Button(self.controls, text="Help", command=self.help)
        self.helpbutton.grid(row=1, column=2, sticky="news")

        #self.run_on_start = [] # Later add run on computer startup
        self.labels = []
        self.run_buttons = []
        self.edit_buttons = []

        self.show_all_data()

    def new(self):
        # User wants to create a new command
        pass

    def help(self):
        pass

    def show_all_data(self):
        for data in self.data:
            run_on_start = data["run_on_start"]
            name = data["name"]
            filename = data["filename"]
            self.show_data(run_on_start, name, filename)

    def show_data(self, run_on_start, name, filename):
        row = len(self.labels)+1

        #run_on_start

        label = tk.Label(self.frame, text=name)
        label.grid(row=row, column=2)
        self.labels.append(label)

        run = tk.Button(self.frame, text="Run", command=partial(self.run, row-1, filename))
        run.grid(row=row, column=3)
        self.run_buttons.append(run)

        edit = tk.Button(self.frame, text="Edit", command=partial(self.edit, row-1, filename))
        edit.grid(row=row, column=4)
        self.edit_buttons.append(run)

    def edit(self, idx, filename):
        pass

    def run(self, idx, filename):
        with open(BASE_DIR+"commands\\"+filename, "r") as file:
            string = file.read()
        try:
            commands = PADDING+"\n\n"+string
            with open(BASE_DIR+"commands\\temp\\temp.py", "w") as file:
                file.write(commands)
            import commands.temp.temp
        except SystemExit:
            # Success
            pass
        except Exception as error:
            # An error occured
            print(error)

    def read(self):
        with open(BASE_DIR+"commands\\tbl.tbl", "r") as file:
            rawdata = file.read()
        self.data = []
        for line in rawdata.split("\n"):
            name, filename, run_on_start, *future = line.split("|")
            if filename != "filename.ext":
                self.data.append({"run_on_start": run_on_start, "name": name, "filename": filename})
    
    def save_new(self, name, contents, run_on_start):
        filename = self.find_untaken_filename()
        with open(BASE_DIR+"commands\\tbl.tbl", "a") as file:
            data = "|".join([name, filename, run_on_start])
            file.write(data+"\n")

    def find_untaken_filename(self):
        for i in range(100000):
            filename = BASE_DIR+"commands\\%i.pyrun"%i
            if not os.path.exists(filename):
                return BASE_DIR+"commands\\%i.pyrun"%i

    def closer(self):
        self.frame.destroy()
        self.controls.destroy()