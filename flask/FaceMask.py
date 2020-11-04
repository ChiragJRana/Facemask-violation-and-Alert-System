# IMporting the libraries
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import imutils
import numpy as np 
import cv2
import os
import  time

class CustomerImage:
    def __init__(self):
        self.proto_txt_path = "../face_detector/deploy.prototxt"
        self.weights_path = "../face_detector/res10_300x300_ssd_iter_140000.caffemodel"
        self.face_net = cv2.dnn.readNet(self.proto_txt_path, self.weights_path)
        self.mask_net = load_model("../face_detector/mask_detector.model")
    
    def detect_and_find_face(self, frame):
        # faceNet is to detect the face and maskNet is the classifier

        (h,w) = frame.shape[:2] # dimensions of the frame
        blob = cv2.dnn.blobFromImage(frame, 1.0, (300,300), (104.0,177.0,123.0))# blob[Binary Large Object] from the frame

        # pass the blob too detect the face 
        self.face_net.setInput(blob)
        detections = self.face_net.forward()

        # list of faces their locations and corresponding predictions
        faces = []
        locs = []
        preds = []
        # print(detections.shape[2])

        # loop over the detections
        for i in range(0, detections.shape[2]):

            # extract the cconfisence i.e probability associated with the detection
            confidence = detections[0,0,i,2]

            # filter the ones whose confidence is greater than min_conf
            if confidence > 0.5:
                
                # compute the x,y coordinates for the box
                box = detections[0, 0, i, 3:7] * np.array([w,h,w,h])

                (start_x, start_y, end_x, end_y) = box.astype('int')


                # ensure the boounding boxes fall within the dimensions of the frame
                (start_x, start_y) = (max(0, start_x), max(0, start_y))
                (end_x, end_y) = (min(w-1, end_x), min(h-1, end_y))

                # extract the roi from the face convert to RGB from RBG and resize to 244X244
                face = frame[start_y:end_y,start_x:end_x]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (244,244))
                face = img_to_array(face)
                face = preprocess_input(face)

                # add the boxes to the list of the faces and the locs 
                faces.append(face)
                locs.append((start_x, start_y, end_x, end_y))


        if len(faces) > 0:
            # making batch predictions on all the faces rather than one by one
            faces = np.array(faces, dtype='float32')
            preds = self.mask_net.predict(faces , batch_size=32)
        
        return (locs, preds)

    
    # def capture_image(self, frame):
        
    #     frame = imutils.resize(frame, width=400)
        
    #     (locs, preds) = self.detect_and_find_face(frame)
        
    #     for (box, pred) in zip(locs, preds):
    #         # unpack the bounding box and predictions
    #         (start_x, start_y, end_x, end_y) = box
    #         (mask, withoutMask) = pred

    #         # determine the class label and color we'll use to draw the bounding box and text
    #         label = "Mask" if mask > withoutMask else "No Mask"
    #         color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
    #         # print(self.limit)
    #         # if label == 'Mask':
    #         #     self.limit = max(self.limit-1,0)

    #         # if label == "No Mask": self.limit = min(20,self.limit + 1)

    #         # if self.limit == 0:
    #         #     self.alarm.stop_alarm()

    #         # if self.limit == 20:
    #         #     self.alarm.ring_alarm()
                
    #         # include the probability in the label
    #         label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

    #         # display the label and bounding box rectangle on the output frame
    #         cv2.putText(frame, label, (start_x, start_y - 10),
    #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
    #         cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, 2)
        
    #     # flip the image as opencv doesnt how mirror image if not included still not a problem
    #     return (cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

