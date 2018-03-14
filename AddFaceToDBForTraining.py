#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 16:11:37 2018




"""

from dbManager import dbManager

def stop(msg='Program exited!'):
    print (msg)
    exit(0)
db=dbManager()
totalPeople=db.execQuery('SELECT COUNT(*) FROM PEOPLE')[0][0]
newID=totalPeople+1
answer=raw_input('The database has %s people.\nThis program will add a new person with ID=%s \nDo you want to continue?' %(str(totalPeople),str(newID)))
if ((answer in ['YES','Y','y','yes','Yes'])==False):
    stop()


print('Anykey to start recording!')
