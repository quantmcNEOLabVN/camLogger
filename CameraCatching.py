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

def checkNewPeople(previousBB,currentBBox,minConfidenceAccepted=0.5):
    if (len(currentBBox)<1):
        return False,[]
    newPeople=[]
    i=0
    j=0
    while (i<len(currentBBox)):
        u=currentBBox[i]
        found=False
        while (j<len(previousBB)):
            v=previousBB[j]
            if (u.faceID>=v.faceID):
                if (u.faceID==v.faceID):
                    found=True
                break
            j=j+1
        if (found==False):
            if (u.confidence<minConfidenceAccepted):
                print ("Low confidence detected, %s  ! Closest person ID is %s" %(str(u.confidence), str(u.faceID)))
                newPeople.append(PredictionResult(0,u.vectorFace,u.vectorFace))
                
        i=i+1
    return len(newPeople)>0 , newPeople

def checkPeopleLeft(previousBB,currentBBox,minConfidenceAccepted=0.5):    
    return checkNewPeople(currentBBox,previousBB,minConfidenceAccepted)

faceMan=FacesManager()
db=dbManager()
minComaprision=1
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
    
    
    bbList[currentIndex]=currentBBox
    distantIndex=(currentIndex-minComaprision-1+maxIndex) % maxIndex
    if (checkNewPeople(bbList[distantIndex],currentBBox)[0]==True):
            print("No. people appeared in camera changed to: "+str(nPeople))
            if (nPeople==0):
                continue 
            now=str(datetime.now())
            now=now.replace("-",'').replace(":",'').replace(".",'').replace(" ",'')
            imgFile=savingImgFolder+now+".png"
            db.execQuery('''  INSERT INTO IMAGES VALUES ('%s', '%s',to_timestamp('%s' , 'YYYYMMDDHH24MISSFF')) ''' %(now,imgFile,now))
            cv2.imwrite(imgFile , frame)
            for faceRes in currentBBox:
                faceMan.addNewFace(faceRes.vectorFace,now,faceRes.faceID);
            db.commit()
            for fRes in currentBBox:
                print ("(id=%s , confidence=%s)" % (str(fRes.faceID), str(fRes.confidence)))

# When everything done, release the capture
cap.release()   
cv2.destroyAllWindows()