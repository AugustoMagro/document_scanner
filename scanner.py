from typing import Tuple
import cv2
import numpy as np
import os
import img2pdf
import PyPDF2
import customtkinter as ck
import tkinter as tk
from tkinter import *
from datetime import datetime
from imutils.perspective import four_point_transform
from PIL import Image, ImageTk
from inputBox import App

WIDTH, HEIGHT = 1980, 1080

class VideoCapture():
    def __init__(self):
        self.cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.document_contour = np.array([[0, 0], [WIDTH, 0], [WIDTH, HEIGHT], [0, HEIGHT]])

        self.videoRecording()

    def image_processing(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 201, 255, cv2.THRESH_BINARY)
        adaptive_result = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 1, 71, 5)
        adaptive_result = cv2.bitwise_not(adaptive_result)
        adaptive_result = cv2.medianBlur(adaptive_result, 3)
        return threshold, adaptive_result

    def scan_detection(self, image, frame):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # blur = cv2.GaussianBlur(gray, (5, 5), 0)
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
    
        cv2.drawContours(frame, [self.document_contour], -1, (0, 255, 0), 3)
    
    def videoRecording(self):
        while self.cap.isOpened():
            _, frame = self.cap.read()
            frame_copy = frame.copy()

            self.scan_detection(frame_copy, frame)

            cv2.imshow("webcam", frame)

            warped = four_point_transform(frame_copy, self.document_contour.reshape(4, 2))
            cv2.imshow("warped", warped)

            process_image, adaptive_process = self.image_processing(warped)
            #cv2.imshow("process image", process_image)
            #cv2.imshow("process image2", adaptive_process)

            key = cv2.waitKey(1) & 0b11111111

            if key == ord("q"):
                self.cap.release()
                cv2.destroyAllWindows()

            if key == ord("s"):
                pdf_bytes = self.convert_image_to_pdf(warped)
                file = open(f"WRAPED_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf", "wb")
                file.write(pdf_bytes)
                file.close()

                pdf_bytes = self.convert_image_to_pdf(warped)
                file = open(f"PROCESS.pdf", "wb")
                file.write(pdf_bytes)
                file.close()
                
                reader = PyPDF2.PdfReader("PROCESS.pdf")
                print(len(reader.pages))
                print(reader.pages[0].extract_text())

            elif key == ord("c"):
                pdf_bytes = self.convert_image_to_pdf(warped)
                tipo = "COMPROVANTE"
                self.get_name(pdf_bytes, tipo)

            elif key == ord("e"):
                pdf_bytes = self.convert_image_to_pdf(warped)
                tipo = "ENVELOPE"
                self.get_name(pdf_bytes, tipo)

            elif key == ord("f"):
                pdf_bytes = self.convert_image_to_pdf(warped)
                tipo = "FICHA"
                self.get_name(pdf_bytes, tipo)

    def convert_image_to_pdf(self, img):
        path_image = f"temp_img.jpg"
        cv2.imwrite(path_image, img)
        image = Image.open(path_image)
        pdf_bytes = img2pdf.convert(image.filename)
        image.close()
        os.remove("temp_img.jpg")
        return pdf_bytes
    
    def get_name(self, pdf_bytes, tipo):        
        App(pdf_bytes, tipo)
    
if __name__ == "__main__":
    VideoCapture()