import tkinter, tkinter.filedialog
from tkinter import *

import threading
import os
import sys
from tkinter import ttk, messagebox

from backend.crawler import write_mail_to_file

DEPARTMENTS = {
    "Architettura": "architettura",
    "Economia": "economia",
    "Economia Aziendale": "economiaaziendale",
    "Giurisprudenza": "https://elearning2.giur.uniroma3.it/",
    "Ingegneria": "ingegneria",
    "Filosofia, Comunicazione e Spettacolo": "filosofiacomunicazionespettacolo",
    # "Lingue, Letterature e Culture Straniere": "http://moodle.llcs.uniroma3.it/",
    "Matematica e Fisica": "matematicafisica",
    "Scienze": "scienze",
    "Scienza della Formazione": "http://formonline.uniroma3.it/",
    "Scienze Politiche": "scienzepolitiche",
    "Studi Umanistici": "studiumanistici",
}


def resource_path(relative_path):
    if (hasattr(sys, "_MEIPASS")):
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class MainWindow(Tk):
    department_combobox: ttk.Combobox
    thread: threading.Thread = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.title("Il Mailinator")
        # self.geometry('350x200')
        self.update()
        self.minsize(self.winfo_width(), self.winfo_height())

        n = tkinter.StringVar()
        self.department_combobox = ttk.Combobox(self, width=27, textvariable=n)

        # Adding combobox drop down list
        self.department_combobox['values'] = list(DEPARTMENTS.keys())
        self.department_combobox.grid(column=1, row=1)

        self.department_combobox.set(list(DEPARTMENTS.keys())[0])

        # region Download Button
        self.find_mail_button = Button(self)
        self.find_mail_button.configure(text="Find Mails", command=self.find_mails_click)
        self.find_mail_button.grid(column=1, row=2)
        # endregion
        # endregion

        self.pack_propagate()

        # start window
        self.mainloop()

    def find_mails_click(self):
        department = self.department_combobox.get()
        if department in DEPARTMENTS:
            if self.thread is None or not self.thread.is_alive():
                self.thread = threading.Thread(target=self.run)
                self.thread.start()

    def run(self):
        self.find_mail_button["state"] = "disabled"

        write_mail_to_file()

        messagebox.showinfo("Finito", "Mail salvate nel file output.csv")

        self.find_mail_button["state"] = "normal"
