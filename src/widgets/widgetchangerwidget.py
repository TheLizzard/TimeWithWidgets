import tkinter as tk

from .widget import Widget


class WidgetChangerWidget(Widget):
    def __init__(self, app):
        app.root.geometry("")
        self.frame = tk.Frame(app.root)
        self.button1 = tk.Button(self.frame, text="DateTime",
                                 command=app.datetimewidget)
        self.button2 = tk.Button(self.frame, text="Alarm",
                                 command=app.alarmwidget)
        self.button3 = tk.Button(self.frame, text="Errors",
                                 command=app.errorswidget)
        self.button4 = tk.Button(self.frame, text="Tasks",
                                 command=app.taskswidget)
                                 
        self.button1.grid(row=1, column=1)
        self.button2.grid(row=1, column=2)
        self.button3.grid(row=1, column=3)
        self.button4.grid(row=1, column=4)

        self.frame.grid(row=1, column=1)

    def closer(self):
        self.frame.destroy()
