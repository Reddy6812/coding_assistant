# coding_assistant.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import pyautogui
import pytesseract
from PIL import Image, ImageGrab, ImageOps
import io
import openai
import keyboard
import numpy as np
import os
from dotenv import load_dotenv

# Configuration
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path

class ScreenSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.3)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        self.canvas = tk.Canvas(self.root, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.start_x = None
        self.start_y = None
        self.rect = None
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        self.selection = None
    
    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=3)
    
    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)
    
    def on_release(self, event):
        x1, y1 = (self.start_x, self.start_y)
        x2, y2 = (event.x, event.y)
        self.selection = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
        self.root.destroy()
    
    def get_selection(self):
        self.root.mainloop()
        return self.selection

class CodingAssistant:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.setup_hotkey()
        
    def setup_hotkey(self):
        keyboard.add_hotkey('ctrl+alt+c', self.process_screen_capture)
        print("Listening for hotkey (Ctrl+Alt+C)... Press Esc to exit.")
        keyboard.wait('esc')

    def process_screen_capture(self):
        print("Select screen area...")
        selector = ScreenSelector()
        region = selector.get_selection()
        
        if region:
            screenshot = self.capture_screen(region)
            text = self.image_to_text(screenshot)
            solution = self.get_chatgpt_solution(text)
            self.show_solution(solution)

    def capture_screen(self, region):
        x1, y1, x2, y2 = region
        screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        return self.preprocess_image(screenshot)

    def preprocess_image(self, image):
        image = image.convert('L')  # Grayscale
        image = ImageOps.invert(image)
        image = image.point(lambda x: 0 if x < 140 else 255)  # Thresholding
        return image

    def image_to_text(self, image):
        return pytesseract.image_to_string(image)

    def get_chatgpt_solution(self, problem_text):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a coding expert. Provide complete, optimized solutions with explanations."},
                    {"role": "user", "content": f"Solve this coding problem:\n\n{problem_text}"}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Error: {str(e)}"

    def show_solution(self, solution):
        window = tk.Tk()
        window.title("Coding Solution")
        
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=100, height=30)
        text_area.insert(tk.INSERT, solution)
        text_area.pack(padx=10, pady=10)
        
        ttk.Button(window, text="Close", command=window.destroy).pack(pady=5)
        window.mainloop()

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("Error: OpenAI API key not found in .env file")
    else:
        CodingAssistant()