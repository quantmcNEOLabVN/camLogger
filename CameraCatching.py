# -*- coding: utf-8 -*-
"""
Spyder Editor
This is a temporary script file.
"""

import openface
import numpy as np
import cv2
from dbManager import *
from FacesManager  import *
from datetime import datetime
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


def checkNewPeople(previousBB,currentBBox,minDAccepted=0.5):
    newPeople=[]
    for u in currentBBox:
        minD=99999999
        for v in previousBB:
            D=u-v
            minD=min(np.dot(D,D),minD)
        if (minD>minDAccepted):
            newPeople.append(u);
    return len(newPeople)>0 , newPeople

def checkPeopleLeft(previousBB,currentBBox,minDAccepted=0.5):
    leftPeople=[]
    for u in previousBB:
        minD=99999999
        for v in currentBBox:
            D=u-v
            minD=min(np.dot(D,D),minD)
        if (minD>minDAccepted):
            leftPeople.append(u)
    return len(leftPeople)>0 , leftPeople

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
    for bb in bboxes:x
        alignedFace = align.align(imgDim, frame,  bb,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        rep2 = net.forward(alignedFace)
        currentBBox.append(rep2)
    bbList[currentIndex]=currentBBox
    distantIndex=(currentIndex-minComaprision-1+maxIndex) % maxIndex
    if (checkNewPeople(bbList[distantIndex],currentBBox)[0]==True):
        checkContinuous=True
        for i in range(1,minComaprision+1):
            idz=(currentIndex - i + maxIndex) % maxIndex
            if ((checkNewPeople(bbList[idz],currentBBox)[0]==True)):
                checkContinuous=False
                break
            if ((checkNewPeople(bbList[idz],bbList[distantIndex])[0]==False)):
                checkContinuous=False
                break
        if (checkContinuous == True):
            print("No. people appeared in camera changed to: "+str(nPeople))
            if (nPeople==0):
                continue
            now=str(datetime.now())
            now=now.replace("-",'').replace(":",'').replace(".",'').replace(" ",'')
            imgFile=savingImgFolder+now+".png"
            db.execQuery('''  INSERT INTO IMAGES VALUES ('%s', '%s',to_timestamp('%s' , 'YYYYMMDDHH24MISSFF')) ''' %(now,imgFile,now))
            cv2.imwrite(imgFile , frame)
            for vecFace in currentBBox:
                faceMan.addNewFace(vecFace,now);
            db.commit()

# When everything done, release the capture
cap.release()   
cv2.destroyAllWindows()