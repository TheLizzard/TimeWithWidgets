from tkinter import ttk
from pathlib import Path
import tkinter as tk
import json
import time
import os

from .widget import Widget
from .notebook import NoteBook


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = str(Path(BASE_DIR).parent)+"\\"


class TasksWidget(Widget):
    def __init__(self, app):
        self.root = app.root
        self.notebook = NoteBook(self.root)
        self.read_tasks()
        self.notebook.grid(row=1, column=1)

        self.control_frame = tk.Frame(self.root)
        self.add_task_button = tk.Button(self.control_frame, text="Add new",
                                         command=self.add_task)
        self.remove_task_button = tk.Button(self.control_frame, text="Remove",
                                            command=self.remove_task)
        self.add_task_button.grid(row=1, column=1, sticky="news")
        self.remove_task_button.grid(row=1, column=2, sticky="news")
        self.control_frame.grid(row=2, column=1)

        self.add_all_tasks()

    def show_task(self, task_name, task_number):
        frame = tk.Frame(self.notebook)
        frame.task_name = task_name
        label = tk.Label(frame, text=task_name)
        label.grid(column=1, row=1)
        self.notebook.append(frame, text="Task "+str(task_number+1))

    def read_tasks(self):
        """
        Read the file and store it in self.json
        """
        with open(BASE_DIR+"Tasks\\tasks.json") as file:
            self.json = json.load(file)
            self.tasks = self.json["tasks"] # Shallow copy

    def save(self):
        with open(BASE_DIR+"Tasks\\tasks.json", "w") as file:
            json.dump(self.json, file, indent=4)

    def add_task(self):
        task_adder = TaskAdder(self.root)
        task_adder.wait() # Waits until the user is done
        task_name = task_adder.get()
        if task_name is not None:
            self.tasks.append(task_name)
            self.show_task(task_name, self.notebook.length())
            self.save()

    def remove_task(self):
        frame = self.notebook.pop_current()
        if frame is None:
            return None
        task_name = frame.task_name
        self.tasks.remove(task_name)

        with open(BASE_DIR+"Tasks\\tasks.json", "w") as file:
            json.dump(self.json, file, indent=4)
        frame.destroy()

    def add_all_tasks(self):
        # print(self.tasks) # Debugging
        for task_number, task_name in enumerate(self.tasks):
            self.show_task(task_name, task_number)

    def closer(self):
        self.notebook.destroy()
        self.control_frame.destroy()

    def window_updater(self):
        pass


class TaskAdder:
    def __init__(self, main_window):
        self.result = None
        self.running = True
        self.main_window = main_window
        self.root = tk.Toplevel(main_window)
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self.cancel)

        self.label_save = ttk.Label(self.root, text="Name of the task")
        self.label_save.grid(row=1, column=1, sticky="news")

        self.user_entry = ttk.Entry(self.root)
        self.user_entry.bind("<Return>", self.done)
        self.user_entry.grid(row=1, column=2, sticky="news")

        self.done_button = ttk.Button(self.root, text="Done", command=self.done)
        self.done_button.grid(row=2, column=1, columnspan=2, sticky="news")

        self.user_entry.focus()

    def cancel(self, event=None):
        self.running = False
        self.result = None
        time.sleep(0.11) # To stop racing conditions
        self.root.destroy()

    def done(self, event=None):
        self.running = False
        result = self.user_entry.get()
        self.root.destroy()
        if result == "":
            return None
        self.result = result

    def wait(self):
        while self.running:
            self.root.update()
            self.main_window.update()
            time.sleep(0.1)

    def get(self):
        return self.result
