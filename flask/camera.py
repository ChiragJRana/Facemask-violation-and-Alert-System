# IMporting the libraries
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import imutils
from imutils.video import VideoStream
import numpy as np 
import cv2
import os
from django.conf import settings
import  time
from .alert import Alarm
from .centroidtracker import CentroidTracker

class CustomerImage:
    def __init__(self, alarm):
        self.prototxtPath = os.path.join(settings.BASE_DIR,'face_detector/deploy.prototxt')
        self.weightsPath = os.path.join(settings.BASE_DIR,'face_detector/res10_300x300_ssd_iter_140000.caffemodel')
        self.faceNet = cv2.dnn.readNet(self.prototxtPath, self.weightsPath)
        self.maskNet = load_model(os.path.join(settings.BASE_DIR,'face_detector/mask_detector.model'))
        self.alarm = alarm
        self.limit = 0
        self.Turned_on = False
        # load the face mask detector model from disk
        print("[INFO] loading face mask detector model...")
        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        self.video = VideoStream(src=0)  
        self.video.stop()
        self.ct = CentroidTracker()



    def start(self):
        self.Turned_on = True
        self.video.start()
        time.sleep(2.0)

    def stop(self):
        if self.Turned_on:
            self.video.stop()
            self.alarm.stop_alarm()
        
        self.Turned_on = False
        
    def detect_and_find_face(self, frame):
        # faceNet is to detect the face and maskNet is the classifier

        (h,w) = frame.shape[:2] # dimensions of the frame
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300,300), (104.0,177.0,123.0))# blob[Binary Large Object] from the frame

        # pass the blob too detect the face 
        self.faceNet.setInput(blob)
        detections = self.faceNet.forward()

        # list of faces their locations and aorresponding predictions
        faces = []
        locs = []
        preds = []

        # loop over the detections
        for i in range(0, detections.shape[2]):

            # extract the cconfisence i.e probability associated with the detection
            confidence = detections[0,0,i,2]

            # filter the ones whose confidence is greater than min_conf
            if confidence > 0.5:
                
                # compute the x,y coordinates for the box
                box = detections[0, 0, i, 3:7] * np.array([w,h,w,h])
                (startX, startY, endX, endY) = box.astype('int')


                # ensure the boounding boxes fall within the dimensions of the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(w-1, endX), min(h-1, endY))

                # extract the roi from the face convert to RGB from RBG and resize to 244X244
                face = frame[startY:endY,startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (244,244))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the boxes to the list of the faces and the locs 
                faces.append(face)
                locs.append((startX, startY, endX, endY))


            if len(faces) > 0:
                # making batch predictions on all the faces rather than one by one
                faces = np.array(faces, dtype='float32')
                preds = self.maskNet.predict(faces , batch_size=32)
            
            return (locs, preds)

    
    def capture_image(self):
        
        frame = self.video.read()
        frame = imutils.resize(frame, width=400)

        (locs, preds) = self.detect_and_find_face(frame)
        
        for (box, pred) in zip(locs, preds):
            # unpack the bounding box and predictions
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            # determine the class label and color we'll use to draw
            # the bounding box and text
            label = "Mask" if mask > withoutMask else "No Mask"
            color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
            print(self.limit)
            if label == 'Mask':
                self.limit = max(self.limit-1,0)

            if label == "No Mask": self.limit = min(20,self.limit + 1)

            if self.limit == 0:
                self.alarm.stop_alarm()

            if self.limit == 20:
                self.alarm.ring_alarm()
                
            # include the probability in the label
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            # display the label and bounding box rectangle on the output frame
            cv2.putText(frame, label, (startX, startY - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
        
        # flip the image as opencv doesnt how mirror image if not included still not a problem
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()




# Unwanted Code for reference

# face_cascade = cv2.CascadeClassifier(os.path.join(settings.BASE_DIR,'cascades/data/haarcascade_frontalface_alt2.xml'))
# profile_face_cascade = cv2.CascadeClassifier('cascades\data\haarcascade_profileface.xml')

# checking the working of the camera =================================================
# print(cv2.__version__)

# cap = cv2.VideoCapture(0) # there is method to select multiplee cameras
# while True : # continuous  read of a frame 
#     ret, frame = cap.read()
#     # convert image to gray 
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     cv2.imshow('frame',gray)
#     cv2.imshow('frame1',frame)
   
#     cv2.waitKey(1)
#     if cv2.waitKey(2) & 0xFF == ord('q'):

#         break
# ====================================================================================


# # Checking the detection working or not==================================================

# # print(help(cv2.face))
# cap = cv2.VideoCapture(0)

# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
	
# 	# convert the grames to gray
#     gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # this method will detect the face and return an object with its dimentions
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5) # for the front face
#     # profile = profile_face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5) # for the side face 
#     # profile_flip = profile_face_cascade.detectMultiScale(cv2.flip(gray,1), scaleFactor=1.5, minNeighbors=5) # for the flipped side face


# # # loop for box around the profile
#     # for (x, y, w, h) in profile:
#     #     print(x,y,w,h)
#     #     roi_gray = gray[y:y+h, x:x+w]
#     #     roi_color = frame[y:y+h, x:x+h]

#     #     img_item = "images/my_image.png"
#     #     cv2.imwrite(img_item, roi_gray)

#     #     # Create a box around the face
#     #     color = (255,0,0)
#     #     stroke = 2

#     #     cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)

# # # loop for box around the flipped-profile

#     # for (x, y, w, h) in profile_flip:
#     #     print(x,y,w,h)
#     #     roi_gray = gray[y:y+h, x:x+w]
#     #     roi_color = frame[y:y+h, x:x+h]

#     #     img_item = "images/my_image.png"
#     #     cv2.imwrite(img_item, roi_gray)

#     #     # Create a box around the face
#     #     color = (255,0,0)
#     #     stroke = 2

#     #     cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)
        

#     for (x, y, w, h) in faces:
        
#         # Create a box around the face
#         color = (255,0,0)
#         stroke = 2

#         cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)

#     # Display the resulting frame
#     cv2.imshow('frame',frame)
#     if cv2.waitKey(20) & 0xFF == ord('q'):
#         break

# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()
# # ========================================================================

# Normal face detection using the inbuild cv2 model.

# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)

#     def __del__(self):
#         self.video.release()

    
#     def get_frame(self):
#         ret, frame = self.video.read()
	
# 	    # convert the grames to gray
#         gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#         # this method will detect the face and return an object with its dimentions
#         faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
#         profile = profile_face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5) # for the side face 
#         profile_flip = profile_face_cascade.detectMultiScale(cv2.flip(gray,1), scaleFactor=1.5, minNeighbors=5) # for the flipped side face
#         print('Streaming_Video')
#         # # loop for box around the profile
#         for (x, y, w, h) in profile:
            
#             # Create a box around the face
#             color = (255,0,0)
#             stroke = 2

#             cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)

#         # loop for box around the flipped-profile

#         for (x, y, w, h) in profile_flip:
            
#             # Create a box around the face
#             color = (255,0,0)
#             stroke = 2

#             cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)

#         #  create the frame for the face the detected only the frontal part.
#         for (x, y, w, h) in faces:

#             # Create a box around the face
#             color = (255,0,0)
#             stroke = 2

#             cv2.rectangle(frame, (x,y), (x+w, y+h), color, stroke)
        
#         # flip the image as opencv doesnt how mirror image if not included still not a problem
#         frame_flip = cv2.flip(frame,1)
#         ret, jpeg = cv2.imencode('.jpg', frame_flip)
#         return jpeg.tobytes()
