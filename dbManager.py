#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 15:37:33 2018

@author: root
"""
import cx_Oracle
class dbManager:

    ip = None
    port = None
    SID = None
    dsn_tns = None
    databaseConnection = None
    def __init__(self,ip='localhost',port=1521,sid='xe',username='camLogger',password='neolabvn'):
        self.ip=ip
        self.port=port
        self.SID=sid
        self.dsn_tns = cx_Oracle.makedsn(self.ip, self.port, self.SID)
        self.databaseConnection = cx_Oracle.connect(username,password, self.dsn_tns)
    def connectDB(self,ip='localhost',port=1521,sid='xe',username='camLogger',password='neolabvn'):
        self.ip=ip
        self.port=port
        self.SID=sid
        self.dsn_tns = cx_Oracle.makedsn(self.ip, self.port, self.SID)
        self.databaseConnection = cx_Oracle.connect(username,password, self.dsn_tns)
        
    def execQuery(self,query):
        if (self.databaseConnection is None):
            self.connectDB()
        cursor = self.databaseConnection.cursor()
        cursor.execute(query)
       
        try:
            return cursor.fetchall()
        except:
            self.commit()
            return None
    def commit(self):
        self.databaseConnection.commit()
