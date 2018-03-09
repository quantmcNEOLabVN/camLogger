# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import openface
import numpy as np
import cv2
from time import sleep
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
multiple = True
imgDim = 96
networkModel = 'openface/models/openface/nn4.small2.v1.t7'
dlibFacePredictor = 'openface/models/dlib/shape_predictor_68_face_landmarks.dat'
align = openface.AlignDlib(dlibFacePredictor)
net = openface.TorchNeuralNet(networkModel, imgDim=imgDim, cuda=False)


    
cap = cv2.VideoCapture(0)
def quit():
    cap.release()
    cv2.destroyAllWindows()


rep1=np.array([0]*128)
n1=0
bb1=[]
bb2=[]
n2=0


maxIndex=24
idx=-1
bbList=[[]] * maxIndex


def checkNewPeople(bb1,bb2):
    
    n=len(bb1)
    m=len(bb2)
    if (n!=m):
        return True
    
    for u in bb2:
        minD=99999999
        for v in bb1:
            D=u-v
            minD=min(np.dot(D,D),minD)
        if (minD>0.3):
            return True
    return False


minComaprision=5

while(True):
    # Capture frame-by-frame
    idx=(idx+1) % maxIndex
    ret, frame = cap.read()
    # Our operations on the frame come here
    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    bboxes = align.getAllFaceBoundingBoxes(frame)
    n2=len(bboxes)
#    print 'No. People in txhe captured image:' + str(n2)
    
    bb2=[]
    for bb in bboxes:
        alignedFace = align.align(imgDim, frame,  bb,
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        rep2 = net.forward(alignedFace)
        bb2.append(rep2)
    bb2=np.array(bb2)
    bbList[idx]=bb2
    if (checkNewPeople(bbList[(idx-minComaprision-1+maxIndex)%maxIndex],bb2)==True):
        checkContinuous=True
        for i in range(1,minComaprision+1):
            if (checkNewPeople(bbList[(idx - i + maxIndex) % maxIndex],bb2)==True):
                checkContinuous=False
                break
        if (checkContinuous == True):
            print("No. people appearred in camera: "+str(len(bb2)))
        
    
#    rep2 obtained similarly.
#    d = rep1 - rep2
#    distance = np.dot(d, d)
#    if (distance>1):
#        rep1=rep2
#        print("New face appeared!")
#        print(rep2)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()