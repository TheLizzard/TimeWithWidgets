exit()
import tkinter as tk
from datetime import datetime
from threading import Thread
import struct
import socket
import time


WEEKDAYNAMES = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]
ZERO_TIME = datetime.utcfromtimestamp(85200)


class Clock:
    def __init__(self, realdatetime=ZERO_TIME):
        self.real = realdatetime
        self.fake = datetime.now()
        self.difference = self.real-self.fake
        self.last_updated = self.real

    def update(self, realdatetime=None):
        self.fake = datetime.now()
        if realdatetime is None:
            self.real = self.fake+self.difference
        else:
            self.last_updated = self.real = realdatetime
            self.difference = self.real-self.fake

    def __str__(self):
        real = self.real
        string = "%s {:02d}/{:02d}/%d {:02d}:{:02d}:{:02d}"
        string = string%(WEEKDAYNAMES[real.weekday()], real.year)
        string = string.format(real.day, real.month,
                               real.hour, real.minute, real.second)
        return string

    def __eq__(self, other):
        return self.get_time() == other

    def __gt__(self, other):
        return self.get_time() > other

    def __lt__(self, other):
        return self.get_time() < other

    def __ge__(self, other):
        return self.get_time() >= other

    def __le__(self, other):
        return self.get_time() <= other

    def get_time(self):
        return "{:02d}:{:02d}".format(self.real.hour, self.real.minute)


class DraggableWindow(tk.Tk):
    def __init__(self):
        self.widgets = []
        self._geometry = ""
        super().__init__()
        self.add_topmost()
        self.reset()
        self._offsetx = 0
        self._offsety = 0
        self.bind("<Control-w>", self.kill)
        self.bind("<Button-1>", self.clickwin)
        self.bind("<Button-2>", self.hide)
        self.bind("<Button-3>", self.reset)
        self.bind("<B1-Motion>", self.dragwin)

    def add_topmost(self):
        self.attributes("-topmost", True)
        try:
            # Linux distributions:
            self.attributes("-type", "splash")
        except:
            # Windows:
            self.overrideredirect(True)

    def hide(self, event=None):
        self.bind("<Button-2>", self.show)
        self.widgets = self.winfo_children()
        for widget in self.widgets:
            widget.grid_remove()
        self._geometry, *geometry = self.winfo_geometry().split("+")
        self.geometry("10x10+"+"+".join(geometry))

    def show(self, event=None):
        self.geometry(self._geometry)
        self.bind("<Button-2>", self.hide)
        for widget in self.widgets:
            widget.grid()

    def reset(self, event=None):
        self.geometry("+0+0")

    def dragwin(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry("+%d+%d"%(x, y))

    def clickwin(self, event):
        self._offsetx = event.x+event.widget.winfo_rootx()-self.winfo_rootx()
        self._offsety = event.y+event.widget.winfo_rooty()-self.winfo_rooty()

    def kill(self, event=None):
        self.quit()
        self.destroy()
        exit()


class App:
    def __init__(self):
        self.root = DraggableWindow()
        self.label = tk.Label(self.root, text="")

        self.label.grid(row=1, column=1)
        self.label_dot = tk.Label(self.root, text="•")
        self.label_dot.grid(row=1, column=2)

        self.clock = Clock()
        self.connection = "red"

    def mainloop(self):
        self.start()
        self.root.mainloop()

    def start(self):
        t = Thread(target=self.update_time)
        t.deamon = True
        t.start()
        self.label_dot.config(fg=self.connection)
        self.clock.update()
        self.label.config(text=str(self.clock))
        self.root.after(1000, self.start)

    def update_time(self, host="time.google.com", port=123):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"\x1b" + 47 * b"\0", (host, port))
            unpacked = struct.unpack("!12I",  s.recvfrom(1024)[0][0:48])
            s.close()
            ntp_time = unpacked[10] + unpacked[11]/4294967296 - 2208988800

            local_datetime = datetime.fromtimestamp(ntp_time)
            self.clock.update(local_datetime)
            self.connection = "green"
        except socket.gaierror:
            diff = self.clock.real-self.clock.last_updated
            not_updated = self.clock.last_updated == ZERO_TIME
            if (diff.days>0) or (diff.seconds>30) or not_updated:
                self.connection = "red"
            else:
                self.connection = "yellow"
        except Exception:
            raise


a = App()
a.mainloop()
