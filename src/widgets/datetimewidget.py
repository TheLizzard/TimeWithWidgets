from datetime import datetime
import tkinter as tk
import struct
import socket

from .widget import Widget


WEEKDAYNAMES = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
ZERO_TIME = datetime.utcfromtimestamp(85200)



class Time:
    def __init__(self, dtime):
        self.second = dtime.second
        self.minute = dtime.minute
        self.hour = dtime.hour

    def __str__(self):
        return "{:02d}:{:02d}:{:02d}".format(self.hour, self.minute,
                                             self.second)

    def update(self, time):
        self.second = time.second
        self.minute = time.minute
        self.hour = time.hour

    @classmethod
    def now(cls):
        return Time(datetime.now())

    @classmethod
    def from_values(cls, hour, minute, second=0):
        out = Time(datetime.now())
        out.second = second
        out.minute = minute
        out.hour = hour
        return out


class Day:
    def __init__(self, dtime):
        self.day = dtime.day
        self.month = dtime.month
        self.year = dtime.year
        self.weekday = dtime.weekday()
        self.weekday_name = WEEKDAYNAMES[self.weekday]

    def __str__(self):
        return self.str()

    def str(self, weekday=True):
        if weekday:
            string = self.weekday_name+" {:02d}/{:02d}/%d"
        else:
            string = "{:02d}/{:02d}/%d"
        string = string.format(self.day, self.month)
        return string%self.year

    def get_as_tuple(self):
        return (self.day, self.month, self.year)

    @classmethod
    def now(cls):
        return Day(datetime.now())

    @classmethod
    def from_values(cls, day, month, year):
        out = Day(datetime.now())
        out.day = day
        out.month = month
        out.year = year
        return out


class DateTimeWidget(Widget):
    def __init__(self, app):
        self.app = app
        self.label = tk.Label(self.app.root, text="")
        self.label.grid(row=1, column=1)
        self.label_dot = tk.Label(self.app.root, text="•", font="bold")
        self.label_dot.grid(row=1, column=2)

        self.time = Time(ZERO_TIME)
        self.day = Day(ZERO_TIME)
        self.connection = "red"

    def updater(self, host="time.google.com", port=123):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"\x1b" + 47 * b"\0", (host, port))
            unpacked = struct.unpack("!12I",  s.recvfrom(1024)[0][0:48])
            s.close()
            ntp_time = unpacked[10] + unpacked[11]/4294967296 - 2208988800

            local_datetime = datetime.fromtimestamp(ntp_time)
            self.time = Time(local_datetime)
            self.day = Day(local_datetime)
            self.connection = "green"
        except socket.gaierror:
            self.connection = "red"

    def window_updater(self):
        self.label.config(text=str(self.day)+" "+str(self.time))
        self.label_dot.config(fg=self.connection)

    def closer(self):
        self.label.destroy()
        self.label_dot.destroy()
