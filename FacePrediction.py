#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 10:12:07 2018

@author: root
"""

import numpy as np
from dbManager import dbManager
from sklearn.svm import SVC
from sklearn.externals import joblib
class PredictionResult:
    faceID=None
    confidence=0
    vectorFace=None
    def __init__(self,ID,conf,vectorFace):
        self.faceID=ID
        self.confidence=conf
        self.vectorFace=vectorFace
    def __repr__(self):
        return ''' (id=%s,   confidence=%s) \n''' %(str(self.faceID),str(self.confidence))

class FacePrediction:
    model = SVC(kernel='linear',probability=True)
    dataX=[]
    dataY=[]
    def __init__(self):
        self.model = SVC(kernel='linear',probability=True)
        self.dataX=[]
        self.dataY=[]
        try:
            self.loadModel()
        except:
            self.loadDataFromDB()
            self.doTrain()
            self.saveModel()

    def addSingleDataSample(self,singleX,singleY):
        self.dataX.append(np.array(singleX))
        self.dataY.append(singleY)

    def addData(self,nX,nY):
        for i in range(len(nX)):
            singleX=nX[i]
            singleY=nY[i]
            self.dataX.append(np.array(singleX))
            self.dataY.append(singleY)
    def loadDataFromDB(self):
        db=dbManager()
        dataSet=db.execQuery('''SELECT VectorFace, Person_ID FROM EMP_IMG WHERE ( Person_ID is not null)''')
        for rec in dataSet:
            self.addSingleDataSample(eval(rec[0]),rec[1])
    def doTrain(self):
        X=np.array(self.dataX)
        Y=np.array(self.dataY)
        self.model.fit(X,Y)
    def saveModel(self,fileName="classifier.sav"):
        joblib.dump(self.model, fileName)
        print("File loaded")
    def loadModel(self,fileName="classifier.sav"):
        joblib.load(self.model, fileName)
    

    def predict(self,X):
        if (len(X)<=0):
            return []
        npX=np.array(X)
        if (len(npX.shape)<=1):
            npX=np.array([npX])            
        Y=[]
        
        y=self.model.predict_proba(npX).tolist()
        x=0
        for res in y:
            maxConFid=-1
            face=0
            for i in range(len(res)):
                if (maxConFid<res[i]):
                    maxConFid=res[i]
                    face=i+1
            Y.append(PredictionResult(face,maxConFid,X[x]))
            x=x+1
        sorted(Y, key=lambda face: face.faceID)  
        return Y
