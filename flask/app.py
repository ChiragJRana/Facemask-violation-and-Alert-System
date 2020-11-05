import threading
from flask import Flask, request, jsonify
import os
from tkinter import *
from PIL import ImageTk, Image
import cv2
import time
# from FaceMask import CustomerImage
# from alert import Alarm

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
stat = False

# Create a Product
@app.route('/', methods=['POST'])
def post_data():
    print(request.get_json())

    return jsonify({'status':'200'})

@app.route('/', methods=['GET'])
def get_data():
    
    return {'status':'200'}


class App:
    def __init__(self,window,window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.t2 = threading.Thread(target=flaskapi, daemon=True)
        self.t2.start()
        # self.video_source = video_source
        # self.alarm = Alarm()
        # self.vid = CustomerImage(alarm = self.alarm,video_source = video_source)
        self.canvas = Canvas(window)
        self.canvas.pack()
        # self.delay = 1
        # self.update()
        self.window.mainloop()

    # def update(self):
    #     frame = self.vid.capture_image()
    #     self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame))
    #     self.canvas.create_image(0,0,image = self.photo, anchor = NW)
    #     self.window.after(self.delay,self.update)
    
    # def __del__(self):
        


def tkinter():
    App(Tk(), "COVID Violation Detect System")

def flaskapi():
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    
if __name__ == '__main__':
    tkinter()
    # t1 = threading.Thread(target=tkinter)
