import tkinter as tk
from datetime import datetime

class App:
    def __init__(self, pdf_bytes, tipo):
        self.back = False
        self.result = ""
        self.pdf_bytes = pdf_bytes
        self.tipo = tipo

        self.HEIGHT = 200
        self.WIDTH = 800   
        self.root = tk.Tk()
        self.root.width = self.WIDTH
        self.root.height = self.HEIGHT
        self.dialogroot = self.root
        self.strDialogResult = ""    
        self.canvas = tk.Canvas(self.root, height=self.HEIGHT, width=self.WIDTH)
        self.canvas.pack()    
        frame = tk.Frame(self.root, bg='#ffffff')
        frame.place(relx=0.5, rely=0.02, relwidth=0.96, relheight=0.95, anchor='n')  

        self.entry = tk.Entry(frame, font=40)
        self.entry.place(relwidth=0.65, rely=0.02, relheight=0.96)
        self.entry.focus_set()

        submit = tk.Button(frame, text='OK', font=16, command=self.DialogResult)
        submit.place(relx=0.7, rely=0.02, relheight=0.96, relwidth=0.3)

        self.root.mainloop()

    def DialogResult(self):
        self.result = self.entry.get()
        file = open(f"{self.tipo}_{self.result}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf", "wb")
        file.write(self.pdf_bytes)
        file.close()
        self.root.destroy()