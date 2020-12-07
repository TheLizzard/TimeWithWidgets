import tkinter as tk


class partial:
    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        out = self.function.__name__+"("
        for arg in self.args:
            out += str(arg)+", "

        for key, value in self.kwargs.items():
            out += str(key)+"="+str(value)+", "

        out = out[:-2]
        return out+")"

    def __call__(self, *args, **kwargs):
        return self.function(*self.args, *args, **self.kwargs, **kwargs)


class NoteBook(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.current_tab = -1
        self.frames = []
        self.buttons = []
        self.names = []
        self.button_frame = tk.Frame(self)
        self.button_frame.grid(row=1, column=1)

    def length(self):
        return len(self.frames)

    def append(self, frame, text="Tab"):
        id = len(self.frames)
        command = partial(self.change_tab, None)
        self.frames.append(frame)
        button = tk.Button(self.button_frame, text=text, command=command,
                           bg="light grey")
        command.args = (button, )
        button.grid(row=1, column=id)
        self.buttons.append(button)
        if self.current_tab == -1:
            self.change_tab(button)

    def change_tab(self, widget):
        idx = self.buttons.index(widget)
        if self.current_tab == idx:
            return None
        if self.current_tab != -1:
            if self.current_tab < len(self.buttons):
                current_frame = self.frames[self.current_tab]
                current_frame.grid_forget()
                old_button = self.buttons[self.current_tab]
                old_button.config(bg="light grey")

        new_frame = self.frames[idx]
        new_frame.grid(row=2, column=1)
        new_button = self.buttons[idx]
        new_button.config(bg="white")

        self.current_tab = idx

    def pop_current(self):
        if self.current_tab == -1:
            return None
        frame = self.frames[self.current_tab]
        del self.frames[self.current_tab]
        button = self.buttons[self.current_tab]
        button.destroy()
        del self.buttons[self.current_tab]
        self.current_tab = -1
        if len(self.buttons) != 0:
            self.change_tab(self.buttons[0])
        return frame


if __name__ == "__main__":
    root = tk.Tk()
    notebook = NoteBook(root)
    notebook.pack()

    frame1 = tk.Frame(notebook)
    label1_f = tk.Label(frame1, text="Frame number 1")
    label1_s = tk.Label(frame1, text="This is some text.")
    label1_f.pack()
    label1_s.pack()
    notebook.append(frame1, text="First Tab")

    frame2 = tk.Frame(notebook)
    label2_f = tk.Label(frame2, text="Frame number 2")
    label2_s = tk.Label(frame2, text="This is some text.")
    label2_f.pack()
    label2_s.pack()
    notebook.append(frame2, text="Second Tab")
