import tkinter as tk
import customtkinter as ck
import cv2
from datetime import datetime
from PIL import Image, ImageTk
from imutils.perspective import four_point_transform
import img2pdf
import PyPDF2
import os
import numpy as np

WIDTH, HEIGHT = 1980, 1080

class App(ck.CTk):
    def __init__(self):
        super().__init__()
        self.back = False
        self.result = ""
        # self.pdf_bytes = pdf_bytes
        # self.tipo = tipo

        self.title("Scanner")
        self.geometry("1920x1080")
        self.grid_columnconfigure((0,1), weight=1, uniform="a")
        self.grid_rowconfigure((0,1), weight=1, uniform="a")

        self.entryBox = ck.CTkEntry(self, placeholder_text="Numero envelope", border_width=0)
        self.entryBox.grid(row=0, column=0, ipadx=20, ipady=17)

        self.frame_buttons = ck.CTkFrame(self)
        self.frame_buttons.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
        self.frame_buttons.grid_columnconfigure(0, weight=1, uniform="a")
        self.frame_buttons.grid_rowconfigure((0,1,2,3), weight=1, uniform="a")

        self.buttonEnvelope = ck.CTkButton(self.frame_buttons, text="Envelope", command=self.buttonEnvelope)
        self.buttonEnvelope.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.buttonFicha = ck.CTkButton(self.frame_buttons, text="Ficha", command=self.buttonFicha)
        self.buttonFicha.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.buttonDt = ck.CTkButton(self.frame_buttons, text="DT", command=self.buttonDt)
        self.buttonDt.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.buttonComprovante = ck.CTkButton(self.frame_buttons, text="Comprovante", command=self.buttonComprovante)
        self.buttonComprovante.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.cap = cv2.VideoCapture(0)
        self.cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.document_contour = np.array([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]])


        self.cam1 = ck.CTkLabel(self)
        self.cam1.grid(row=1, column=0, sticky="nsew")
        
        self.cam2 = ck.CTkLabel(self)
        self.cam2.grid(row=1, column=1, sticky="nsew")

        self.updateImage()

        self.mainloop()

    def updateImage(self):
        ret, frame = self.cap.read()
        frame_copy = frame.copy()

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
            self.cam1.configure(image=self.photo)
            
            self.scan_detection(frame_copy, frame)

        self.after(10, self.updateImage)

    def scan_detection(self, image, frame):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
        contours, _ = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.015 * peri, True)
                if area > max_area and len(approx) == 4:
                    self.document_contour = approx
                    max_area = area

        cv2.drawContours(frame, [self.document_contour], -1, (0, 1, 0), 3)

        self.warped = four_point_transform(frame, self.document_contour.reshape(4, 2))
        self.photo2 = ImageTk.PhotoImage(image=Image.fromarray(self.warped))
        self.cam2.configure(image=self.photo2)

    def convert_image_to_pdf(self, img):
        path_image = f"src/temp_img.jpg"
        cv2.imwrite(path_image, img)
        image = Image.open(path_image)
        pdf_bytes = img2pdf.convert(image.filename)
        image.close()
        # os.remove("src/temp_img.jpg")
        return pdf_bytes

    def DialogResult(self, nome):
        pdf_bytes = self.convert_image_to_pdf(self.warped)
        file = open(f"{nome}_{self.entryBox.get().strip()}_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf", "wb")
        file.write(pdf_bytes)
        file.close()

    def buttonEnvelope(self):
        self.DialogResult("ENVELOPE")

    def buttonFicha(self):
        self.DialogResult("FICHA")

    def buttonDt(self):
        self.DialogResult("DT")
    
    def buttonComprovante(self):
        self.DialogResult("COMPROVANTE")

if __name__ == '__main__':
    app = App()