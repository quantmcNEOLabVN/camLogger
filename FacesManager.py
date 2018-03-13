#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 16:40:14 2018

@author: root
"""

import numpy as np
from dbManager import dbManager
class FacesManager:
    db=dbManager()
    class Face:
        ID=None
        Profile=None
        VectorFace=None
        db=None
        def __init__(self,db,iden,vectorFace,profile=None):
            self.db=db
            self.ID=iden
            self.Profile=profile
            self.VectorFace=vectorFace
        def getProfile(self):
            if (self.ID is None):
                return None
            prof=self.db.execQuery(''' SELECT * FROM EMPLOYEES WHERE (EMPLOYEES.Emp_ID = %s) '''  %str(self.ID));
            if (len(prof)>0):
                self.Profile=prof[0]
            else:
                self.Profile=None
            return self.Profile
        def saveToDB(self):
            if (self.ID is None):
                return None
            self.db.execQuery(''' INSERT INTO PEOPLE VALUES (%s , '%s') ''' %(str(self.ID), str(self.VectorFace.tolist())))
    faceSet=[]
    def loadFacefromDB(self):
        people = self.db.execQuery('''SELECT * FROM PEOPLE''')
        self.faceSet=[]
        for rec in people:
            self.faceSet.append( self.Face(self.db,  rec[0], np.array( eval(rec[1]))))
        return self.faceSet
    def __init__(self):
        self.db=dbManager()
        self.faceSet=[]
        self.loadFacefromDB()

    def findFaceID(self, vectFace,minDAccepted=0.5):
        retID=None
        minD=1000.0
        for face in self.faceSet:
            vf=face.VectorFace
            d = vf - vectFace
            dist=np.dot(d,d)
            if (minD>dist):
                minD=dist
                retID=face.ID
        print minD
        if (minD>minDAccepted):
            return None
        else:
            return retID
    def addNewFace(self, vectFace,imgID):
        pID=self.findFaceID(vectFace)
    
        if (pID is None):
            pID=self.db.execQuery('''SELECT NVL(MAX(Person_ID),0) FROM PEOPLE''')[0][0]+1
            face=self.Face(self.db,pID,vectFace)
            face.saveToDB()
            self.faceSet.append(face)
            print ("New person detected! new ID=%s" %str([pID]))
            
        vectorF="null";
        if (not (vectFace is None)):
             vectorF=str(vectFace.tolist())
        query=''' INSERT INTO EMP_IMG VALUES ( (SELECT COUNT(*)+1 FROM EMP_IMG) , %s, '%s' , '%s') ''' %(str(pID),imgID,vectorF)
        self.db.execQuery(query)
        return True