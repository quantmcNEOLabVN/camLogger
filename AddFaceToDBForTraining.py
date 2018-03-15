#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 16:11:37 2018

"""

from datetime import datetime
import openface
import numpy as np
import cv2
from dbManager import dbManager
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
def stop(msg='Program stopped!'):
    print (msg)
    exit(0)
def quit():
    cap.release()
    cv2.destroyAllWindows()
    

db=dbManager()
totalPeople=db.execQuery('SELECT COUNT(*) FROM PEOPLE')[0][0]
print ("As now, in DB we'have %s people" %str(totalPeople))
for record in db.execQuery('''SELECT pp.PERSON_ID, count(*) FROM PEOPLE pp JOIN  EMP_IMG ei ON (pp.Person_ID=ei.Person_ID) GROUP BY pp.PERSON_ID'''):
    print (''' id=%s: %s samples.''' %(str(record[0]), str(record[1])))


print("Enter an ID in range 1..%s,   %s means add samples with a new person." %(str(totalPeople+1),str(totalPeople+1)))
selectedID=eval(raw_input('Selected ID = '))

if (isinstance(selectedID, (int, long))==False):
    stop("Invalid input.")
if (((1<=selectedID) and (selectedID <= (totalPeople+1)))==False):
    stop("Invalid input.")

isNewPerson=(selectedID>totalPeople)

vectList=[]
if (isNewPerson==False):
    for record in db.execQuery('''SELECT VectorFace FROM EMP_IMG WHERE PERSON_ID=%s''' %(str(selectedID))):
        vectList.append(np.array(eval(record[0])))
print ('Loaded all old samples!')
predictor=FacePrediction()
def checkNewVector(newVector, minDAccepted=0.2, desiredConfidence=0.7):
    global selectedID,vectList,predictor,totalPeople
    if (isNewPerson==False):
        pred=predictor.predict(newVector)[0]
        if ((pred.faceID!=selectedID) or (pred.confidence<desiredConfidence)):
            return True
    else:
        D=99999.0
        for vect in vectList:
            D=min(D, np.dot(vect,newVector))
        if (D>minDAccepted):
            return True

    return False
    
raw_input("Please make sure only the correct person appear in camera!\nHit enter to start recording! Press 'q' to stop recording!")
while (True):
    frame = cap.read()[1]
    # Our operations on the frame come here
    # Display the resulting frame

    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    bboxes = align.getAllFaceBoundingBoxes(frame)
    if (len(bboxes)<1):
        continue
    alignedFace = align.align(imgDim, frame,  bboxes[0],
                landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    vectFace = net.forward(alignedFace)
        
    if (checkNewVector(vectFace)==True):
        if (len(vectList)<1):
            db.execQuery('''INSERT INTO PEOPLE VALUES (%s,'%s')''' %(str(selectedID),str(vectFace.tolist())))
        now=str(datetime.now())
        now=now.replace("-",'').replace(":",'').replace(".",'').replace(" ",'')
        imgFile=savingImgFolder+now+".png"
        db.execQuery('''  INSERT INTO IMAGES VALUES ('%s', '%s',to_timestamp('%s' , 'YYYYMMDDHH24MISSFF')) ''' %(now,imgFile,now))
        cv2.imwrite(imgFile , frame)
        query=''' INSERT INTO EMP_IMG VALUES ( (SELECT COUNT(*)+1 FROM EMP_IMG) , %s, '%s' , '%s') ''' %(str(selectedID),now,str(vectFace.tolist()))
        db.execQuery(query)
        db.commit()
        print ('   Added a new sample for id= %s' %str(selectedID))

cap.release()
cv2.destroyAllWindows()

print("Recording stopped!\nNow we have %s samples for id=%s\n Re-train classifier...." %(str(len(vectList)),str(selectedID)))

predictor.clearDataAndModel()
predictor.loadDataFromDB()
predictor.doTrain()
predictor.saveModel()
print ('Done!\nTesting model with new samples: ')
pred=predictor.predict(vectList)
for result in pred:
    verdict='Wrong ID'
    if (result.faceID==selectedID):
        verdict='Correct ID, with confidence = '+str(result.confidence)
    print(verdict)
    