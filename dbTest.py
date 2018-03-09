#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 15:37:33 2018

@author: root
"""

import cx_Oracle
ip = 'localhost'
port = 1521
SID = 'xe'
dsn_tns = cx_Oracle.makedsn(ip, port, SID)

db = cx_Oracle.connect('camLogger', 'neolabvn', dsn_tns)
cursor = db.cursor()
print (cursor.execute("SELECT * FROM DUAL").fetchall()[0])
print "Query sucessfully executed!"