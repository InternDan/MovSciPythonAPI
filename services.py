import cv2
import numpy as np
import sys
import os
import time
from os import listdir
import math as Math
import boto3
import botocore
import configs

def GetFile(file_path_key):
    BUCKET_NAME = configs.bucket_name # replace with your bucket name
    KEY = file_path_key # replace with your object key
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, KEY)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
    return KEY

def UploadFile(file_path_key):
    s3 = boto3.client('s3')

    filename = file_path_key
    bucket_name = configs.bucket_name

    # Uploads the given file using a managed uploader, which will split up large
    # files automatically and upload parts in parallel.
    try:
        s3.upload_file(filename, bucket_name, filename)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":#update to correct codes
            print("The object does not exist.")
        else:
            raise

def ParseArguments(argv):
    ptsx = []
    ptsy = []
    ptstype = []
    ptscolor = []
    numArgs = len(argv)
    ct=0
    for i in range(0,numArgs):
        if ct == 0:
            ct = 1
            ptstype.append(argv[i])
            continue
        if ct == 1:
            ct = 2
            ptscolor.append(argv[i])
            continue
        if ct == 2:
            ct = 3
            ptsx.append(int(argv[i]))
            continue
        if ct == 3:
            ct = 0
            ptsy.append(int(argv[i]))
            continue
    return ptstype,ptscolor,ptsx,ptsy

def TrackPoints(prevImgGray,currImgGray,ptsTracked,lkparams,numPoints,ptscolor,ptstype):#,

    #pull out last set of coordinates based on number of number of points
    pts = ptsTracked[-numPoints*2:]
    append = []
    
    for i in range(0,len(pts)-1,2):
        #get this type right
        p0 = np.array([[np.float32(pts[i]),np.float32(pts[i+1])]])
        p1, st, err = cv2.calcOpticalFlowPyrLK(prevImgGray, currImgGray, p0, None, **lkparams) 
        p1 = p1.ravel()

        for ii in range(0,len(p1)):
            append = np.append(append,p1[ii])#removed int conversion

    ptsTracked = np.append(ptsTracked,append,axis=0)
    return ptsTracked

def DrawPoints(currImg,ptsTracked,ptscolor,ptstype,numPoints):
    pts = ptsTracked[-numPoints*2:]
    a = np.size(pts,0)
    colCount = 0
    colLen = len(ptscolor)
    i=0
    while i < a:
        if ptstype[colCount] == 'pt':
            currImg = cv2.circle(currImg,(int(pts[i]),int(pts[i+1])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            i += 2
            if colCount == colLen:
                colCount = 0
            continue
        elif ptstype[colCount] == 'ln':
            currImg = cv2.circle(currImg,(int(pts[i]),int(pts[i+1])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+2]),int(pts[i+3])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.line(currImg,(int(pts[i]),int(pts[i+1])),(int(pts[i+2]),int(pts[i+3])),(255,255,0),5)
            i += 4
            if colCount == colLen:
                colCount = 0
            continue
        elif ptstype[colCount] == 'ang2':#TODO - add angle calculation and drawing
            currImg = cv2.circle(currImg,(int(pts[i]),int(pts[i+1])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+2]),int(pts[i+3])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.line(currImg,(int(pts[i]),int(pts[i+1])),(int(pts[i+2]),int(pts[i+3])),(0,255,255),5)
            dy = pts[3] - pts[1]
            dx = pts[2] - pts[0]
            angle = Math.degrees(abs(Math.atan2(dy,dx)))
            if angle >= 180:
                angle = 360 - angle
            currImg = cv2.putText(currImg,str(int(angle)),(int(pts[i]+10),int(pts[i+1]+10)),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),2,cv2.LINE_AA)
            i += 4
            if colCount == colLen:
                colCount = 0
            continue
        elif ptstype[colCount] == 'ang3':#TODO - reorganize to match angle
            currImg = cv2.circle(currImg,(int(pts[i]),int(pts[i+1])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+2]),int(pts[i+3])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+4]),int(pts[i+5])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.line(currImg,(int(pts[i]),int(pts[i+1])),(int(pts[i+2]),int(pts[i+3])),(0,255,255),5)
            currImg = cv2.line(currImg,(int(pts[i]),int(pts[i+1])),(int(pts[i+4]),int(pts[i+5])),(0,255,255),5)
            angle = Math.degrees(Math.atan2(pts[5] - pts[1], pts[4] - pts[0]) - Math.atan2(pts[3] - pts[1], pts[2] - pts[0]));
            angle = abs(angle)
            if angle >= 180:
                angle = 360 - angle
            currImg = cv2.putText(currImg,str(int(angle)),(int(pts[i]+10),int(pts[i+1]+10)),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),2,cv2.LINE_AA)
            i += 6
            if colCount == colLen:
                colCount = 0
            continue
        elif ptstype[colCount] == 'ang4':#TODO - add angle calculation and drawing
            currImg = cv2.circle(currImg,(int(pts[i]),int(pts[i+1])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+2]),int(pts[i+3])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+4]),int(pts[i+5])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.circle(currImg,(int(pts[i+6]),int(pts[i+7])),20,eval(ptscolor[colCount]),6,1)
            colCount += 1
            currImg = cv2.line(currImg,(int(pts[i]),int(pts[i+1])),(int(pts[i+2]),int(pts[i+3])),(0,255,255),5)
            currImg = cv2.line(currImg,(int(pts[i+4]),int(pts[i+5])),(int(pts[i+6]),int(pts[i+7])),(0,255,255),5)
            angle1 = Math.atan2(pts[5] - pts[7],pts[4] - pts[6])
            angle2 = Math.atan2(pts[1] - pts[3],pts[0] - pts[2])
            angle = Math.degrees(abs(angle1-angle2))
            if angle >= 180:
                angle = abs(360 - angle)
            else:
                angle = abs(angle)
            currImg = cv2.putText(currImg,str(int(angle)),(int(pts[i]+10),int(pts[i+1]+10)),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,255),2,cv2.LINE_AA)
            i += 8
            if colCount == colLen:
                colCount = 0
            continue
    return currImg