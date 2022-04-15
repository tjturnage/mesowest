#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 21:30:11 2019

@author: tj

"""


def timeShift(timeStr,num,dt,direction):
    times = []
    steps = int(num)
    minStart = int(steps * dt)
    initTime = datetime.strptime(timeStr,'%Y%m%d%H%M')
    if direction == 'backward':
        origTime = initTime - timedelta(minutes=minStart)
    else:
        origTime = initTime   

    for x in range(0,steps):
        mins = x * dt
        newTime = origTime + timedelta(minutes=mins)
        nextTime = newTime + timedelta(minutes=dt)
        newStr = datetime.strftime(newTime, '%Y%m%d%H%M')
        new = datetime.strftime(newTime, '%Y-%m-%dT%H:%M:%SZ')
        nextTimeStr = datetime.strftime(nextTime, '%Y-%m-%dT%H:%M:%SZ')
        times.append([newStr,new,nextTimeStr])
    return times




def convertVal(num,short):
    numfloat = float(num)
    if (num != 'NA' ):

        if short == 'wgst':
            new = int(round(numfloat,1))
            newStr = str(new)
        elif short == 'wspd':
            new = int(round(numfloat,1))
            newStr = str(new)
        else:
            pass

        return newStr


    
def getData(timeStr, archive):
    if archive == 'Y':
        api_arguments = {"token":API_TOKEN,"state":"mi","network":"1,2,71,96,162,3001", "vars": varStr, "units": unitsStr, 'attime': timeStr, 'within':'10' }
        #api_arguments = {"token":API_TOKEN,"cwa":"bmx", "vars": varStr, "units": unitsStr, 'attime': timeStr, 'within':'40' }
        api_request_url = os.path.join(API_ROOT, "stations/nearesttime")
    else:
        api_arguments = {"token":API_TOKEN,"state":"mi,wi","network":"1,2,71,96,162,3001", "vars": varStr, "units": unitsStr}
        api_request_url = os.path.join(API_ROOT, "stations/latest")

    req = requests.get(api_request_url, params=api_arguments)
    jas = req.json()
    return jas
    
#import json

import os
import sys

try:
    os.listdir('/var/www')
    windows = False
    sys.path.append('/data/scripts/resources')
    image_dir = os.path.join('/var/www/html/radar','images')
except:
    windows = True
    sys.path.append('C:/data/scripts/resources')
    base_dir = 'C:/data'
    image_dir = os.path.join('C:/data','images')

import math
import requests

#from pandas import DataFrame
from datetime import datetime, timedelta

formatT = "%Y-%m-%dT%H:%M:%SZ"

shortDict = {'air_temp_value_1':'t',
             'dew_point_temperature_value_1d':'dp',
             'wind_speed_value_1':'wspd',
             'wind_direction_value_1':'wdir',
             'wind_gust_value_1':'wgst',
             'visibility_value_1':'vis',
             'road_temp_value_1':'rt'
             }

shortDict = {'wind_speed_value_1':'wspd',
             'wind_direction_value_1':'wdir',
             'wind_gust_value_1':'wgst'}
           


stnDict2 = {'t':{'threshold':100,'color':'200 100 100','position':'-17,13, 1,'},
          'dp':{'threshold':100,'color':'0 255 0','position':'-17,-13, 1,'},
          'wspd':{'threshold':500,'color':'255 255 255','position':'NA'},
          'wdir':{'threshold':500,'color':'255 255 255','position':'NA'},
          'wgst':{'threshold':300,'color':'255 255 255','position':'NA'},
          'vis':{'threshold':125,'color':'180 180 255','position':'17,-13, 1,'},
          'rt':{'threshold':125,'color':'255 255 0','position':'17,13, 1,'}}


#varStr = 'visibility,road_temp'
varStr = 'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,visibility,road_temp'
unitsStr = 'temp|F,speed|kts,precip|in'

varList =[]
for keys in shortDict:
    varList.append(str(keys))

#https://developers.synopticdata.com/about/station-variables/
#https://synopticlabs.org/demos/lookup/?&lookup=networks

API_ROOT = "https://api.synopticdata.com/v2/"
from mesowest_api_token import API_TOKEN

nowTime_now = datetime.utcnow() - timedelta(minutes=60)
nowTime = nowTime_now.replace(minute=56)
nowTimeStr = datetime.strftime(nowTime,'%b %d,%Y %H:%M UTC')
nowTimeStr2 = datetime.strftime(nowTime,'%Y%m%d%H%M')

archive = 'Y'
#timeStr = '201909120200'
timeStr = nowTimeStr2
dt = 180
niceTime = timeStr[0:4] + '-' + timeStr[4:6] + '-' + timeStr[6:8] + '-' + timeStr[-4:]  
num = 6
numMin = str(dt * num)
#placeFileName = 'latest_surface_observations.txt'
placeFileName = 'Surface obs_' + niceTime + '_' + numMin + 'minutes.txt'
placeTitle = 'Surface obs_' + niceTime + '_' + numMin + 'minutes'
if archive != 'Y':
    num = 1

    csvFile = 'lon,lat,wspd,wgst\n'

direction = 'backward' # 'forward'
times = timeShift(timeStr,num,dt,direction)

csvFile = 'lon,lat,name,vsby,roadt\n'
placefile = 'Title: Mesowest ' + placeTitle + '\nRefresh: 2\nColor: 255 200 255\n \
IconFile: 1, 18, 32, 2, 31, "https://mesonet.agron.iastate.edu/request/grx/windbarbs.png" \n \
IconFile: 2, 15, 15, 8, 8, "https://mesonet.agron.iastate.edu/request/grx/cloudcover.png"\n \
IconFile: 3, 25, 25, 12, 12, "https://mesonet.agron.iastate.edu/request/grx/rwis_cr.png"\n \
Font: 1, 14, 1, "Arial"\n\n'

obsDict = {}

for t in range(0,len(times)):
    jas = getData(timeStr, archive)
    if archive == 'Y':
        timeStr = times[t][0]
        now = times[t][1]
        future = times[t][2]
        timeText = 'TimeRange: ' + now + ' ' + future + '\n\n'
        placefile = placefile + timeText
        
    for j in range(0,len(jas['STATION'])):
        tempTxt = ''
        stid = (jas['STATION'][j]['STID'])
        lon = (jas['STATION'][j]['LONGITUDE'])
        lat = (jas['STATION'][j]['LATITUDE'])
        status = (jas['STATION'][j]['STATUS'])
        wdirStr = 'NA'
        wspdStr = 'NA'
        wgstStr = 'NA'

        if (status == 'ACTIVE') and str(stid) in ['KGRR','KMKG']:
            for k in range(0,len(varList)):
                thisVar = str(varList[k])
                short = str(shortDict[thisVar])
                try:
                    scratch = jas['STATION'][j]['OBSERVATIONS'][thisVar]['value']

                    if short == 'wspd':
                        wspdStr = convertVal(scratch,short)

                    elif short == 'wdir':
                        wdirStr = convertVal(scratch,short)
                        
                    elif short == 'wgst':
                        wgstStr = convertVal(scratch,short)
            
                except:
                    pass


        #tempTxt = tempHead + '  Threshold: 100\n' + dpTxt + ' End:\n\n'
        if wgstStr != 'NA':
            tempcsv = str.join(' ', [timeStr[0:4],timeStr[4:6],timeStr[6:8],timeStr[8:10],'00',str(stid),wspdStr,wgstStr])
            print(tempcsv)
        #placefile = placefile + tempTxt

"""
try:
    os.chdir('C:/data/scripts/')
except:
    webDir = '/var/www/html/placefiles/'
else:
    webDir = 'C:/data/'

dstFile = webDir + placeFileName
dst2File = webDir + 'vsby.csv'
with open(dstFile, 'w') as outfile:
    outfile.write(placefile)
with open(dst2File, 'w') as outfile:
    outfile.write(csvFile)

TimeRange: 2019-03-06T23:14:39Z 2019-03-06T23:16:29Z

"""