import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import cv2
import numpy as np
from flask import Flask, request, jsonify
from FaceMask import CustomerImage
from alert import Alarm
from imagesearch.centroidtracker import CentroidTracker
import imutils
import time
import threading
import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
stat = False
alarm = Alarm()
password = 'password'
maxlimit = 2
LARGE_FONT = ("Verdana", 12)

@app.route('/', methods=['POST'])
def post_data():
    msg = "No changes"
    
    request_dictt = request.get_json()
    print(request_dictt)
    if request_dictt['password'] == password and request_dictt['username'] != '':
        if request_dictt['status'] == 0:
            msg = alarm.work_off()
        else:
            msg = alarm.work_on()
    else:
        return jsonify({'status': msg,'message': 'password is incorrect Please check with the Admin'}), 200
    return jsonify({'message':  'Alarm status changed', "status": msg}),200

@app.route('/', methods=['GET'])
def get_data():
    return {'status':'200'}

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,"Group C2")
        self.t2 = threading.Thread(target=app.run,kwargs={'host':"0.0.0.0", 'port':5000, 'debug':True, 'use_reloader':False}, daemon=True)
        self.t2.start()
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}

        for f in (StartPage, ImagePage):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)

        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        self.parent = parent
        label = ttk.Label(self, text = "Welcome to the Face Mask Detection Application", font = LARGE_FONT)
        label.pack(pady=15, padx=20)
        self.entry = ttk.Entry(self)
        self.entry.insert(10,password)    
        self.entry.pack(padx=10, pady=20)
        button2 = ttk.Button(self, text= "Change Password", command=self.changepassword)
        button2.pack(side = tk.TOP, pady= 10)
        self.entry1 = ttk.Entry(self)
        self.entry1.insert(10,maxlimit)    
        self.entry1.pack(padx=10, pady=20)
        button3 = ttk.Button(self, text= "Enter the number of people Allowed", command=self.setMaxLimit)
        button3.pack(side = tk.TOP, pady= 10)
        button1 = ttk.Button(self, text= "Go to the Camera Recording", command=lambda: controller.show_frame(ImagePage))
        button1.pack(side = tk.TOP, pady= 10)
        
    def changepassword(self):
        global password
        password = self.entry.get()
        print(password)

    def setMaxLimit(self):
        global maxlimit
        maxlimit = int(self.entry1.get())

    def __del__(self):
        tk.Frame.__delattr__(self,self.parent)
    

class ImagePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        
        #  ======================== Attaching the Alarm , Image, Canvas =====================================
        self.alarm = alarm
        self.facemask = CustomerImage()
        self.tracker = CentroidTracker()

        # ==================================== Widgets ======================================================  
        self.canvas = tk.Canvas(self, bg="black")
        self.default_image = Image.open("default.png")
        self.frame = self.default_image
        self.width = 640
        self.height = 380

        self.canvas.configure(width = self.width, height = self.height)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.canvas.bind('<Configure>', self._resize_image)
        button1 = ttk.Button(self, text= "Go back", command=lambda: controller.show_frame(StartPage))
        button1.pack(side = tk.RIGHT, padx = 10, pady = 10)
        self.StartButton = ttk.Button(self,text="Start The Recording", command= self.start_recording)
        self.StartButton.pack(side = tk.LEFT, padx = 10, pady = 10)
        
        # ========================== Additional   Variables =================================================
        self.people_limit = 0
        self.mask_limit = 0
        self.recording = False
        self.update()
        
    def start_recording(self):
        # print(self.recording)
        if not self.recording:
            self.vid = cv2.VideoCapture(0,cv2.CAP_DSHOW)
            # self.width = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
            # self.height = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            # print(self.width, self.height)
        
            if not self.vid.isOpened():
                raise ValueError("Unable to open video source", 0)
            self.recording = True
            self.StartButton['text'] = "Stop The Recording"
            # print(self.StartButton['text'])
            self.update()
        else:
            self.recording = False
            self.StartButton['text'] = "Start The Recording"
            self.vid.release()
            self.alarm.stop_alarm()
            

    def capture_image(self):
        
        if self.vid.isOpened():
            ret, frame = self.vid.read()

        if ret:
            
            (locs, preds) = self.facemask.detect_and_find_face(frame)
            objects = self.tracker.update(locs)

            ObjectIDs =  objects.keys()
            centroids = objects.values()
            print(self.mask_limit, self.people_limit)
            if len(preds) > maxlimit:
                self.people_limit = min(self.people_limit+1,15)
            else:
                self.people_limit = max(0, self.people_limit-1)
            
            if len(preds) == 0:
                self.mask_limit = 0
                self.people_limit = 0
                self.alarm.stop_alarm()

            if not self.alarm.alarm_switch and self.people_limit == 15:
                self.takeSnapShot()
                self.alarm.ring_alarm()
            
            if self.alarm.alarm_switch and self.people_limit == 0 and self.mask_limit == 0:
                    self.alarm.stop_alarm()
            without_mask = 0

            for (box, pred, ObjectID, centroid) in zip(locs, preds, ObjectIDs, centroids):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                # determine the class label and color we'll use to draw the bounding box and text
                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                
                if label == "No Mask": 
                    without_mask += 1
                
                if not self.alarm.alarm_switch and  self.mask_limit == 15:
                    self.takeSnapShot()
                    self.alarm.ring_alarm()
                # include the probability in the label
                
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)
                
                color_id = (0, 255, 0)
                if len(ObjectIDs) > maxlimit:
                    color_id = (0,0,255)

                text = "ID {}".format(ObjectID+1)
                cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_id, 2)
                cv2.circle(frame, (centroid[0], centroid[1]), 4, color_id, -1)
                
                # display the label and bounding box rectangle on the output frame
                cv2.putText(frame, label, (startX, startY - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            self.frame = frame
            if without_mask > 0:
                self.mask_limit = min(15,self.mask_limit + 1)
            else:
                self.mask_limit = max(0,self.mask_limit-1)
                
            # Return a boolean success flag and the current frame converted to BGR
            return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            
        return (None, None)
    
    def _resize_image(self,event):

        self.width = event.width
        self.height = event.height
        print('New height:', self.height, 'new width:', self.width)
        if not self.recording:
            image_copy  = self.default_image.copy()
            self.photo = ImageTk.PhotoImage(image_copy.resize((self.width,self.height), Image.ANTIALIAS))
            self.canvas.create_image(2, 2, image = self.photo, anchor ='nw')

    def update(self):
        if self.recording:
            ret, frame = self.capture_image()
            if ret:
                self.photo = ImageTk.PhotoImage(image = Image.fromarray(frame).resize((self.width,self.height), Image.ANTIALIAS))
                self.canvas.create_image(2, 2, image = self.photo, anchor ='nw')
                self.after(15,self.update)
        else:
            self.photo = ImageTk.PhotoImage(image =Image.open("default.png").resize((self.width,self.height), Image.ANTIALIAS))
            self.canvas.create_image(2, 2, image = self.photo, anchor ='nw')

    def takeSnapShot(self):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d`_%H-%M-%S"))         
        cv2.imwrite('D:/SADproject/flask/proofs/' + filename, self.frame)
        
    def __del__(self):
        tk.Frame.__delattr__(self,self.parent)
        if self.vid.isOpened():
            self.vid.release()


if __name__ == '__main__':
    app = Application()
    ttk.Style().configure("TButton", padding=6, relief="flat",background="#ccc")
    app.mainloop()