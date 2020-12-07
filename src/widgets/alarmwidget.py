from tkcalendar import Calendar
from datetime import datetime
from copy import deepcopy
from pathlib import Path
import tkinter as tk
import os.path
import time
import os

from .widget import Widget
from .datetimewidget import Day, Time, WEEKDAYNAMES
from .notebook import NoteBook


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = str(Path(BASE_DIR).parent)+"\\"


class SelectTime(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.hour = tk.Spinbox(self, from_=0, to=23, wrap=True, width=2)
        self.min = tk.Spinbox(self, from_=0, to=59, wrap=True, width=2)
        self.sec = tk.Spinbox(self, from_=0, to=59, wrap=True, width=2)

        self.hour.grid(row=1, column=1)
        self.min.grid(row=1, column=2)
        self.sec.grid(row=1, column=3)

    def __str__(self):
        return "%s:%s:%s"%(self.hour.get(), self.min.get(), self.sec.get())


class SelectDate:
    def __init__(self, default_date, callback=None):
        self.callback = callback
        self.root = tk.Toplevel()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.bind("<Button-1>", self.update)
        self.root.attributes("-topmost", True)
        self.running = True
        self.root.title("Select a date")
        self.root.resizable(False, False)

        day, month, year = default_date.get_as_tuple()

        self.calendar = Calendar(self.root, showweeknumbers=False,
                                 showothermonthdays=False, year=year,
                                 background="#f0f0ed", foreground="black",
                                 mindate=datetime.now(), day=day, month=month,
                                 headersbackground="#f0f0ed")
        self.calendar.calevent_create(datetime.now(),
                                      "Today's date", "today")
        self.calendar.tag_config("today", background="red", foreground="yellow")
        self.calendar.grid(row=1, column=1, sticky="news")

    def get(self):
        celection = self.calendar.selection_get()
        date = Day.from_values(celection.day, celection.month, celection.year)
        return date

    def close(self):
        self.running = False

    def update(self, event):
        if self.callback is not None:
            self.callback(self.get())

    def wait(self):
        self.root.update()
        if self.running:
            self.root.after(100, self.wait)
        else:
            self.root.destroy()


class SelectDateEntry(tk.Text):
    def __init__(self, master):
        super().__init__(master, height=1, width=10, state="disabled")
        self.datechooser = None
        self.date = Day.now()
        self.bind("<Button-1>", self.show)
        self.update(self.date)

    def show(self, event=None):
        if self.datechooser is None:
            self._show()
        elif not self.datechooser.running:
            self._show()
        return "break"

    def _show(self):
        self.datechooser = SelectDate(self.date, callback=self.update)
        self.datechooser.wait()

    def hide(self, event=None):
        if self.datechooser is not None:
            self.datechooser.close()
            self.datechooser = None

    def update(self, new_date):
        self.date = new_date
        self.config(state="normal")
        self.delete("0.0", "end")
        self.insert("0.0", str(new_date))
        self.config(state="disabled")


class AlarmCreator:
    def __init__(self):
        self.done = False
        self.root = tk.Toplevel()
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._done)

        self.day_chooser = SelectDateEntry(self.root)
        self.time_chooser = SelectTime(self.root)
        self.name = tk.Text(self.root, width=23, height=1)
        self.details = tk.Text(self.root, width=23, height=3)
        self.done_button = tk.Button(self.root, text="Done", command=self._done)

        self.day_chooser.grid(row=1, column=1, sticky="news")
        self.time_chooser.grid(row=2, column=1)
        self.name.grid(row=3, column=1, sticky="news")
        self.details.grid(row=4, column=1, sticky="news")
        self.done_button.grid(row=5, column=1, sticky="news")

        self.root.bind("<Button-1>", self.day_chooser.hide)

    def _done(self):
        self.done = True

    def wait(self):
        while not self.done:
            self.root.update()
            time.sleep(0.2)
        self.date = self.day_chooser.get("0.0", "end")
        for weekday in WEEKDAYNAMES:
            self.date = self.date.replace(weekday, "")
        self.date.strip()
        self.time = str(self.time_chooser)
        self.name = self.name.get("0.0", "end")
        self.text = self.details.get("0.0", "end")
        self.root.destroy()

    def get(self):
        name = self.name.replace("\n", "")
        return Alarm(self.date, self.time, name, self.text)


class Alarm:
    def __init__(self, date, time, name, text):
        self.date = self.parse_date(date)
        self.time = self.parse_time(time)
        self.name = name
        self.text = text

    def parse_date(self, rawdate):
        date = map(int, rawdate.split("/"))
        return Day.from_values(*date)

    def parse_time(self, rawtime):
        time = map(int, rawtime.split(":"))
        return Time.from_values(*time)

    def __str__(self):
        out = "Alarm(date=%s, time=%s, name=\"%s\", text=\"%s\")"
        out %= (str(self.date), str(self.time), self.name, self.text)
        return out


class AlarmWidget(Widget):
    def __init__(self, app):
        self.app = app
        self.disable_drag()
        self.alarms = {}
        self.new_alarms = []
        self.update_alarms()
        self.notebook = NoteBook(app.root)
        self.notebook.grid(row=1, column=1)

        self.control_frame = tk.Frame(app.root)
        self.add_button = tk.Button(self.control_frame, text=" + ",
                                    command=self.add)
        self.del_button = tk.Button(self.control_frame, text=" - ",
                                    command=self.sub)
        self.cha_button = tk.Button(self.control_frame, text="Change",
                                    command=self.change)
        self.add_button.grid(row=1, column=1, sticky="news")
        self.del_button.grid(row=1, column=2, sticky="news")
        self.cha_button.grid(row=1, column=3, sticky="news")
        self.control_frame.grid(row=2, column=1)

    def sub(self):
        frame = self.notebook.pop_current()
        if frame is None:
            return None
        id = frame.id
        frame.destroy()
        os.remove(BASE_DIR+"alarms/"+str(id)+".txt")

    def add(self):
        new_alarm = AlarmCreator()
        new_alarm.wait()
        alarm = new_alarm.get()

        date = alarm.date.str(weekday=False)
        time = str(alarm.time)
        name = alarm.name
        details = alarm.text

        data = "%s\n%s\n%s\n%s"%(date, time, name, details)
        id = self.id_not_taken()

        with open(BASE_DIR+"alarms/%i.txt"%id, "w") as file:
            file.write(data[:-1])

        self.alarms.update({alarm: id})
        self.new_alarms.append(alarm)

    def id_not_taken(self):
        for i in range(100000):
            filename = BASE_DIR+"alarms/%i.txt"%i
            if not os.path.exists(filename):
                return i

    def change(self):
        pass

    def update_alarms(self):
        for filename in os.listdir(BASE_DIR+"alarms"):
            filename = filename.replace(".txt", "")
            if filename.isdigit():
                self.update_alarm(filename)

    def update_alarm(self, filename):
        with open(BASE_DIR+"alarms/"+filename+".txt", "r") as file:
            data = file.read()
        data = data.split("\n")
        data = data[:3]+["\n".join(data[3:])]
        alarm = Alarm(*data)
        self.alarms.update({alarm: filename})
        self.new_alarms.append(alarm)

    def window_updater(self):
        alarms = []
        while len(self.new_alarms) > 0:
            alarms.append(self.new_alarms.pop())
        self.new_alarms = []
        alarms.reverse()
        for alarm in alarms:
            frame = tk.Frame(self.notebook)
            frame.id = self.alarms[alarm]
            self.notebook.append(frame, text=alarm.name)

            date = tk.Label(frame, text=str(alarm.date))
            date.grid(row=1, column=1)

            time = tk.Label(frame, text=str(alarm.time))
            time.grid(row=2, column=1)

            other_details = tk.Text(frame, bg="#f0f0ed", width=25, height=3,
                                    borderwidth=0)
            other_details.tag_configure("center", justify="center")
            other_details.insert("0.0", alarm.text)
            other_details.tag_add("center", "0.0", "end")
            other_details.config(state="disabled")
            other_details.grid(row=3, column=1)

    def disable_drag(self):
        self.app.root.draggable = False

    def closer(self):
        self.app.root.draggable = True
        self.notebook.destroy()
        self.control_frame.destroy()
