import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import cv2
from FaceMask import CustomerImage
from alert import Alarm
import imutils
import time
import datetime
import os

LARGE_FONT = ("Verdana", 12)

class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.wm_title(self,"Group C2")
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        for f in (StartPage, PageOne):
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

        self.parent =parent
        
        label = ttk.Label(self, text = "Welcome to the Face Mask Detection Application", font = LARGE_FONT)
        label.pack(pady=15, padx=30)

        button1 = ttk.Button(self, text= "Start The Camera Recording", command=lambda: controller.show_frame(PageOne))
        button1.pack()
        
    def __del__(self):
        tk.Frame.__delattr__(self,self.parent)
    
    

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        #  ======================== Attaching the Alarm , Image, Canvas =====================================
        self.alarm = Alarm()
        self.facemask = CustomerImage()
        # self.vid = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        # self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        # self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # print(self.height, self.width)
        # ==================================== Widgets ======================================================  
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.configure(width = 640, height = 380)
        self.canvas.pack(side="top", fill="both", expand=True)
        button1 = ttk.Button(self, text= "Go back", command=lambda: controller.show_frame(StartPage))
        button1.pack()
        self.StartButton = ttk.Button(self,text="Start The Recording", command= self.start_recording)
        self.StartButton.pack()
        # ========================== Additional   Variables =================================================
        self.delay = 15
        self.limit = 0
        self.count = 0
        self.recording = False
        self.update()
        
    def start_recording(self):
        print(self.recording)
        if not self.recording:
            self.vid = cv2.VideoCapture(0,cv2.CAP_DSHOW)
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(self.width, self.height)
        
            if not self.vid.isOpened():
                raise ValueError("Unable to open video source", 0)
            self.recording = True
            self.StartButton['text'] = "Stop The Recording"
            print(self.StartButton['text'])
            self.update()
        else:
            self.recording = False
            self.StartButton['text'] = "Start The Recording"
            self.vid.release()
            self.alarm.stop_alarm()
            

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            

            if ret:
                (locs, preds) = self.facemask.detect_and_find_face(frame)
                
                if len(preds) >= 3 and not self.alarm.alarm_switch and self.limit == 40:
                        self.takeSnapShot()
                        self.alarm.ring_alarm()
                        self.limit = 0

                for (box, pred) in zip(locs, preds):
                    # unpack the bounding box and predictions
                    (startX, startY, endX, endY) = box
                    (mask, withoutMask) = pred

                    # determine the class label and color we'll use to draw the bounding box and text
                    label = "Mask" if mask > withoutMask else "No Mask"
                    color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                    
                    if label == 'Mask':
                        self.limit = max(self.limit-1,0)

                    if label == "No Mask": 
                        self.limit = min(40,self.limit + 1)
                        

                    if self.alarm.alarm_switch and self.limit == 0:
                        self.alarm.stop_alarm()

                    if not self.alarm.alarm_switch and  self.limit == 40:
                        self.takeSnapShot()
                        self.alarm.ring_alarm()
                        self.limit = 0
                        
                    # include the probability in the label
                    label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                    # display the label and bounding box rectangle on the output frame
                    cv2.putText(frame, label, (startX, startY - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                    cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)
    

    def update(self):
        if self.recording:
            ret, self.frame = self.get_frame()
            if ret:
                self.photo = ImageTk.PhotoImage(image = Image.fromarray(self.frame).resize((640,380), Image.ANTIALIAS))
                self.canvas.create_image(2, 2, image = self.photo, anchor ='nw')
                self.after(1,self.update)

        else:
            self.photo = ImageTk.PhotoImage(Image.open("default.png").resize((640,380), Image.ANTIALIAS))
            self.canvas.create_image(2, 2, image = self.photo, anchor ='nw')

    def takeSnapShot(self):
        # if self.count ==20:
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))         
        cv2.imwrite('proofs/' + filename, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))
        # self.count = 0
        # self.count += 1

    def __del__(self):
        tk.Frame.__delattr__(self,self.parent)
        if self.vid.isOpened():
            self.vid.release()


if __name__ == '__main__':
    app = Application()
    app.mainloop()