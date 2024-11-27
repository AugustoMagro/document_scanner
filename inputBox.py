import tkinter as tk
import customtkinter as ck
from datetime import datetime

class App(ck.CTk):
    def __init__(self, pdf_bytes, tipo):
        super().__init__()
        self.back = False
        self.result = ""
        self.pdf_bytes = pdf_bytes
        self.tipo = tipo

        self.title("Scanner")
        self.geometry("300x180")
        self.grid_columnconfigure(0, weight=1, uniform="a")
        self.grid_rowconfigure((0, 1), weight=1, uniform="a")

        self.entryBox = ck.CTkEntry(self, placeholder_text="Numero envelope", border_width=0)
        self.entryBox.grid(row=0, column=0, ipadx=20, ipady=17)

        self.button = ck.CTkButton(self, text="my button", command=self.DialogResult)
        self.button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.mainloop()

    def DialogResult(self):
        self.result = self.entryBox.get()
        file = open(f"{self.tipo}_{self.result}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf", "wb")
        file.write(self.pdf_bytes)
        file.close()
        self.destroy()