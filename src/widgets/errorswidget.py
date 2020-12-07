import traceback
import tkinter as tk

from .widget import Widget
from .notebook import NoteBook


class ErrorsWidget(Widget):
    def __init__(self, app):
        self.app = app
        self.root = self.app.root
        self.root.geometry("10x10")
        self.notebook = NoteBook(self.root)
        self.notebook.grid(row=1, column=1)
        self.frames = []
        self.errorid = 0
        self.skipped = 0
        self.tracebacks = []

    def updater(self):
        pass

    def window_updater(self):
        while len(self.app.errors) > self.errorid+self.skipped:
            traceback = self.app.errors[self.errorid]
            if traceback in self.tracebacks:
                self.skipped += 1
            else:
                self.root.geometry("")
                self.tracebacks.append(traceback)
                frame = tk.Frame(self.notebook)

                t_label = tk.Label(frame, text=traceback)
                t_label.pack(expand=True, fill="both")

                self.notebook.append(frame, text=str(self.errorid))
                self.frames.append(frame)
                self.errorid += 1

    def closer(self):
        self.root.geometry("")
        self.notebook.destroy()
