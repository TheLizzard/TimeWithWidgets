from datetime import datetime
from threading import Thread
import tkinter as tk
import traceback

from widgets.datetimewidget import DateTimeWidget
from widgets.widgetchangerwidget import WidgetChangerWidget
from widgets.alarmwidget import AlarmWidget
from widgets.errorswidget import ErrorsWidget


class DraggableWindow(tk.Tk):
    def __init__(self, interrupt):
        self.draggable = True
        self.widgets = []
        self._geometry = ""
        super().__init__()
        self.topmost()
        self.reset()
        self._offsetx = 0
        self._offsety = 0
        self.bind("<Control-w>", self.kill)
        self.bind("<Button-1>", self.clickwin)
        self.bind("<Button-2>", self.hide)
        self.bind("<Button-3>", self.reset)
        self.bind("<B1-Motion>", self.dragwin)
        self.bind("<space>", interrupt)

    def topmost(self):
        self.attributes("-topmost", True)
        try:
            self.attributes("-type", "splash") # Linux
        except:
            self.overrideredirect(True) # Windows

    def hide(self, event=None):
        self.bind("<Button-2>", self.show)
        self.geometry("10x10")

    def show(self, event=None):
        self.geometry("")
        self.bind("<Button-2>", self.hide)

    def reset(self, event=None):
        self.geometry("+0+0")

    def dragwin(self, event):
        if not self.draggable:
            return None
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry("+%d+%d"%(x, y))

    def clickwin(self, event):
        if not self.draggable:
            return None
        self._offsetx = event.x+event.widget.winfo_rootx()-self.winfo_rootx()
        self._offsety = event.y+event.widget.winfo_rooty()-self.winfo_rooty()

    def kill(self, event=None):
        self.quit()
        self.destroy()
        exit()


class App:
    def __init__(self):
        self.root = DraggableWindow(self.changewidget)
        self.root.report_callback_exception = self.exception
        self.widget = None
        self.errors = []
        self.changewidget()

    def exception(self, *args):
        tback = "".join(traceback.format_exception(*args))
        self.errors.append(tback)

    def mainloop(self):
        self.start()
        self.root.mainloop()

    def start(self):
        t = Thread(target=self.updater)
        t.daemon = True
        t.start()
        self.window_updater()
        self.root.after(500, self.start)

    def datetimewidget(self):
        self.closer()
        self.widget = DateTimeWidget(self)

    def alarmwidget(self):
        self.closer()
        self.widget = AlarmWidget(self)

    def errorsidget(self):
        self.closer()
        self.widget = ErrorsWidget(self)

    def starter(self):
        if self.widget is not None:
            self.widget.starter(self)

    def updater(self):
        if self.widget is not None:
            self.widget.updater()

    def window_updater(self):
        if self.widget is not None:
            self.widget.window_updater()

    def closer(self):
        if self.widget is not None:
            self.widget.closer()

    def changewidget(self, *args):
        self.closer()
        self.widget = WidgetChangerWidget(self)

    def errorswidget(self, *args):
        self.closer()
        self.widget = ErrorsWidget(self)


a = App()
try:
    a.mainloop()
except Exception as error:
    a.errors.append(traceback.format_exc())
