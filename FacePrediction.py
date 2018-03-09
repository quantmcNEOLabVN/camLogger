#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 10:12:07 2018

@author: root
"""

import numpy as np
from sklearn import svm
from dbManager import dbManager
import numpy as np
from sklearn.svm import SVC
class FacePrediction:
    model = SVC(kernel='linear')
    dataX=[]
    dataY=[]
    def __init__(self):
        self.model = SVC(kernel='linear')
        self.dataX=np.array([])
        self.dataY=np.array([])


    def addSingleDataSample(self,singleX,singleY):
        self.dataX.append(eval(singleX))
        self.dataY.append(eval(singleY))

    def addData(self,nX,nY):
        self.dataX.append(singleX) 
        self.dataY.append(singleY) 
        
    def loadDataFromDB():
        db=dbManager()
        dataSet=db.execQuery('''SELECT VectorFace, Person_ID FROM EMP_IMG''')
        for rec in dataSet:
            self.addSingleDataSample(rec[0],rec[1])
        
    def doTrain(self):
        X=np.array(dataX)
        Y=np.array(dataY)
        model.fit(X,Y)
    def saveModel(self,fileName="classifier.sav"):
        joblib.dump(self.model, fileName)
    def loadModel(self,fileName="classifier.sav"):
        joblib.dump(self.model, fileName)
        
    def predict(self,X):
        npX=np.array(X)
        Y=self.model.predict(npX)
        return Y