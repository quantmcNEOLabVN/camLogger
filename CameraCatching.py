# -*- coding: utf-8 -*-

import openface
import numpy as np
import cv2
from dbManager import *
from FacesManager  import *
from datetime import datetime
from FacePrediction import *
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
multiple = True
imgDim = 96
networkModel = 'openface/models/openface/nn4.small2.v1.t7'
dlibFacePredictor = 'openface/models/dlib/shape_predictor_68_face_landmarks.dat'
align = openface.AlignDlib(dlibFacePredictor)
net = openface.TorchNeuralNet(networkModel, imgDim=imgDim, cuda=False)


savingImgFolder='capturedPics/'
    
cap = cv2.VideoCapture(0)
def quit():
    cap.release()
    cv2.destroyAllWindows()

maxIndex=24
currentIndex=-1
bbList=[[]] * maxIndex
facePredictor=FacePrediction()

minConfidenceAccepted=0.5
def checkChangeBB(previousBB,currentBBox,minConfidenceAccepted=minConfidenceAccepted,printLowConfidence=False):
    if (len(previousBB)!=len(currentBBox)):
        return True
    if (len(currentBBox)==0):
        return False
    newPeople=[]
    i=0
    while (i<len(currentBBox)):
        u=currentBBox[i]
        v=previousBB[i]
        if (u.faceID!=v.faceID):
            return True
        if (u.confidence<minConfidenceAccepted):
            if (printLowConfidence==True):
                print ("Low confidence detected, %s  ! Closest person ID is %s" %(str(u.confidence), str(u.faceID)))        
        i=i+1
    return False

faceMan=FacesManager()
db=dbManager()
minComaprision=5

while(True):
    # Capture frame-by-frame
    currentIndex=(currentIndex+1) % maxIndex
    frame = cap.read()[1]
    # Our operations on the frame come here
    # Display the resulting frame

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    bboxes = align.getAllFaceBoundingBoxes(frame)
    nPeople=len(bboxes)
    currentBBox=[]
    for bb in bboxes:
        alignedFace = align.align(imgDim, frame,  bb,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        rep2 = net.forward(alignedFace)
        currentBBox.append(rep2)
    currentBBox=facePredictor.predict(currentBBox)
    sorted(currentBBox, key=lambda face: face.faceID)    

    addToDB=False
    bbList[currentIndex]=currentBBox
    distantIndex=(currentIndex-minComaprision-1+maxIndex) % maxIndex
    if (checkChangeBB(bbList[distantIndex],currentBBox)==True):
        print ("Face changing detected!")
        checkContinuous=True
        for i in range(1,minComaprision+1):
            if (checkChangeBB(bbList[(distantIndex+i)%maxIndex],currentBBox,printLowConfidence=True)==True):
                checkContinuous=False
                print ("Face changing rejected! Not continuous enough!")
                break

        if (checkContinuous==True):
            print ("Face changing accepted!")
            if (nPeople==0):
                print ("No face detected!")
                continue 
            now=str(datetime.now())
            now=now.replace("-",'').replace(":",'').replace(".",'').replace(" ",'')
            imgFile=savingImgFolder+now+".png"
            db.execQuery('''  INSERT INTO IMAGES VALUES ('%s', '%s',to_timestamp('%s' , 'YYYYMMDDHH24MISSFF')) ''' %(now,imgFile,now))
            cv2.imwrite(imgFile , frame)
            for faceRes in currentBBox:
                fID=faceRes.faceID
                if (faceRes.confidence<minConfidenceAccepted):
                    fID=None
                faceMan.addNewFace(faceRes.vectorFace,now,faceRes.faceID)
            db.commit()
            addToDB=True
    if (addToDB==True):
        print("Added to database: ")
        for fRes in currentBBox:
            print ("  +    (id=%s , confidence=%s)" % (str(fRes.faceID), str(fRes.confidence)))
        print("------ END LIST ------")
    else:
        for fRes in currentBBox:
           print ("  -    (id=%s , confidence=%s)" % (str(fRes.faceID), str(fRes.confidence)))


# When everything done, release the capture
cap.release()   
cv2.destroyAllWindows()