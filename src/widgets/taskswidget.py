import json,os
from pathlib import Path
from .widget import Widget
from .notebook import NoteBook
import tkinter as tk
from tkinter import ttk

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = str(Path(BASE_DIR).parent)+"\\"

class taskswidget(Widget):
    def __init__(self, app):
        app.root.geometry("")
        self.master = app.root
        self.frame = NoteBook(app.root)
        self.Tasks = []
        self.frames = []
        self.update()
        self.frame.grid(row=1, column=1)

    def taskAddbutton(self):
        addTask(self.master,self)
        
    def update(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        with open(BASE_DIR+"alarms/tasks.json") as opFile:
            self.json = json.load(opFile)

        self.Tasks = self.json["tasks"]
        print(self.Tasks)

        temp = 0
        for x,y in enumerate(self.Tasks):
            self.frames.append(indivTaskFrame(self.frame,y,x))
            temp = x

        self.button = tk.Button(self.frame,command = self.taskAddbutton,text = "add item")
        self.button.grid(row = (temp+1),column = 0)

    def closer(self):
        self.master.geometry("")
        self.frame.destroy()

class indivTaskFrame:
    def __init__(self,frame,text,row,column=0):
        self.frame = tk.Frame(frame)
        self.ob = text
        self.text = tk.Label(self.frame,text=text)
        self.removeButton = tk.Button(self.frame,text = "remove",command = self.destroy)

        self.text.grid(column=0,row=0)
        self.removeButton.grid(column=1,row=0)

        self.frame.grid(row=row,column=column)

        
    def destroy(self):
        self.frame.destroy()
        with open(BASE_DIR+"alarms/tasks.json") as opFile:

            self.json = json.load(opFile)
            self.json["tasks"].pop(self.json["tasks"].index(self.ob))

        with open(BASE_DIR+"alarms/tasks.json","w") as opFile:
            json.dump(self.json,opFile,indent=4)

class addTask:
    def __init__(self,master,obj):
        self.obj = obj
        with open(BASE_DIR+"alarms/tasks.json") as opfile:
            self.store = json.load(opfile)
			
        self.master = master
        self.window = tk.Toplevel(self.master)


        self.LabelSave = ttk.Label(self.window,text="new item")
        self.LabelSave.grid(column=0,row=0)

        self.userEntry = ttk.Entry(self.window)
        self.userEntry.bind("<Return>",lambda thing: self.save())
        self.userEntry.grid(column=1,row=0)

        self.savestore = ttk.Button(self.window,text="Add",command=self.save)
        self.savestore.grid(column=0,row=1)

        self.userEntry.focus()


    def save(self):
        self.store["tasks"].append(self.userEntry.get())
        self.userEntry.delete(0,tk.END)

        with open(BASE_DIR+"alarms/tasks.json","w") as opfile:
            json.dump(self.store,opfile)
        
        self.obj.update()
