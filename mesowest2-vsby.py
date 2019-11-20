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


def placefileWindSpeedCode(wspd):
    speed = float(wspd)
    if speed > 52:
        code = '11'
    elif speed > 47:
        code = '10'
    elif speed > 42:
        code = '9'
    elif speed > 37:
        code = '8'
    elif speed > 32:
        code = '7'
    elif speed > 27:
        code = '6'
    elif speed > 22:
        code = '5'
    elif speed > 17:
        code = '4'
    elif speed > 12:
        code = '3'
    elif speed > 7:
        code = '2'
    elif speed > 2:
        code = '1'
    else:
        code = '1'
    return code


def convertVal(num,short):
    numfloat = float(num)
    if (num != 'NA' ):
        if (short == 't') or (short == 'dp') or (short == 'rt'):
            new = int(round(numfloat))
            newStr = '" ' + str(new) + ' "'
            textInfo = buildObject(newStr,short)
        elif short == 'wgst':
            new = int(round(numfloat,1))
            newStr = '" ' + str(new) + ' "'        
            textInfo = buildObject(newStr,short)
            newStr = str(new)
        elif short == 'vis':
            #print (numfloat)
            final = '10'
            if numfloat < 6.5:
                final = str(int(round(numfloat)))
            if numfloat <= 2.75:
                final = '2 3/4'
            if numfloat <= 2.50:
                final = '2 1/2'                
            if numfloat <= 2.25:
                final = '2 1/4'
            if numfloat <= 2.0:
                final = '2'
            if numfloat <= 1.75:
                final = '1 3/4'                 
            if numfloat <= 1.50:
                final = '1 1/2'                 
            if numfloat <= 1.25:
                final = '1 1/4'
            if numfloat <= 1.00:
                final = '1'
            if numfloat <= 0.75:
                final = '3/4'                   
            if numfloat <= 0.50:
                final = '1/2'
            if numfloat <= 0.25:
                final = '1/4'
            if numfloat <= 0.125:
                final = '1/8'
            if numfloat == 0.0:
                final = ''
            newStr = '" ' + final + ' "'        
            textInfo = buildObject(newStr,short)
        elif short == 'wspd':
            new = placefileWindSpeedCode(numfloat)
            newStr = str(new)
            textInfo = 'ignore'
        elif short == 'wdir':
            new = int(num)
            newStr = str(new)
            textInfo = 'ignore'

        return newStr, textInfo

def gustObj(wdir, wgst, short):
    wgstInt = int(wgst)
    newStr = '" ' + str(wgstInt) + ' "'
    direction = int(wdir)
    distance = 35
    x = math.sin(math.radians(direction)) * distance
    y = math.cos(math.radians(direction)) * distance
    loc = str(int(x)) + ',' + str(int(y)) + ',1,'
    threshLine = 'Threshold: ' + str(stnDict2[short]['threshold']) + '\n'
    colorLine = '  Color: ' + str(stnDict2[short]['color']) + '\n'
    position = '  Text: ' + loc + newStr + ' \n'
    textInfo = threshLine + colorLine + position
    return textInfo

def buildObject(newStr,short):
    threshLine = 'Threshold: ' + str(stnDict2[short]['threshold']) + '\n'
    colorLine = '  Color: ' + str(stnDict2[short]['color']) + '\n'
    position = '  Text: ' + str(stnDict2[short]['position']) + newStr + '\n'
    textInfo = threshLine + colorLine + position
    return textInfo
    
def getData(timeStr, archive):
    if archive == 'Y':
        api_arguments = {"token":API_TOKEN,"state":"mi","network":"1,2,71,96,162,3001", "vars": varStr, "units": unitsStr, 'attime': timeStr, 'within':'30' }
        #api_arguments = {"token":API_TOKEN,"cwa":"bmx", "vars": varStr, "units": unitsStr, 'attime': timeStr, 'within':'40' }
        api_request_url = os.path.join(API_ROOT, "stations/nearesttime")
    else:
        api_arguments = {"token":API_TOKEN,"state":"mi,wi","network":"1,2,71,96,162,3001", "vars": varStr, "units": unitsStr}
        api_request_url = os.path.join(API_ROOT, "stations/latest")

    req = requests.get(api_request_url, params=api_arguments)
    jas = req.json()
    return jas
    
#import json
import math
import requests
import os
#from pandas import DataFrame
from datetime import datetime, timedelta

formatT = "%Y-%m-%dT%H:%M:%SZ"

shortDict = {'air_temp_value_1':'t',
             'dew_point_temperature_value_1d':'dp',
             'wind_speed_value_1':'wspd',
             'wind_direction_value_1':'wdir',
             'wind_gust_value_1':'wgst',
             'visibility_value_1':'vis',
             'road_temp_value_1':'rt'}

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
API_TOKEN = "292d36a692d74badb6ca011f4413ae1b"

nowTime = datetime.utcnow()
nowTimeStr = datetime.strftime(nowTime,'%b %d,%Y %H:%M UTC')
nowTimeStr2 = datetime.strftime(nowTime,'%Y%m%d%H%M')

archive = 'Y'
timeStr = '201909120200'
#timeStr = nowTimeStr2
dt = 5
niceTime = timeStr[0:4] + '-' + timeStr[4:6] + '-' + timeStr[6:8] + '-' + timeStr[-4:]  
num = 36
numMin = str(dt * num)
#placeFileName = 'latest_surface_observations.txt'
placeFileName = 'Surface obs_' + niceTime + '_' + numMin + 'minutes.txt'
placeTitle = 'Surface obs_' + niceTime + '_' + numMin + 'minutes'
if archive != 'Y':
    num = 1
    placeFileName = 'Road_Temps_and_Visibilities.txt'
    placeTitle = 'Road Temp and Visibility ' + nowTimeStr
    csvFile = 'lon,lat,vsby,rtemp\n'

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
        lon = (jas['STATION'][j]['LONGITUDE'])
        lat = (jas['STATION'][j]['LATITUDE'])
        status = (jas['STATION'][j]['STATUS'])
        tStr = 'NA'
        dpStr = 'NA'
        wdirStr = 'NA'
        wspdStr = 'NA'
        wgstStr = 'NA'
        visStr = 'NA'
        rtStr = 'NA'
        if (status == 'ACTIVE'):
            for k in range(0,len(varList)):
                thisVar = str(varList[k])
                short = str(shortDict[thisVar])
                try:
                    scratch = jas['STATION'][j]['OBSERVATIONS'][thisVar]['value']
                    if short == 't':
                        tStr, textInfo = convertVal(scratch,short)
                        tTxt = tempTxt + textInfo
                    elif short == 'dp':
                        dpStr, textInfo = convertVal(scratch,short)
                        dpTxt = tempTxt + textInfo
                    elif short == 'rt':
                        rtStr, textInfo = convertVal(scratch,short)
                        rtTxt = tempTxt + textInfo
                    elif short == 'vis':
                        visStr, textInfo = convertVal(scratch,short)
                        visTxt = tempTxt + textInfo
                    elif short == 'wspd':
                        wspdStr, val = convertVal(scratch,short)
                    elif short == 'wdir':
                        wdirStr, val = convertVal(scratch,short)                    
                    elif short == 'wgst':
                        wgstStr, textInfo = convertVal(scratch,short)
                        wgstTxt = tempTxt + textInfo                
                except:
                    pass

        objHead = 'Object: '  + lat + ',' + lon + '\n'     

        if wdirStr != 'NA' and wspdStr != 'NA':
            windTxt = objHead + '  Threshold: 500\n  Icon: 0,0,' + wdirStr + ',1,' + wspdStr + '\n End:\n\n'
            placefile = placefile + windTxt

        if tStr != 'NA' and dpStr != 'NA':
            placefile = placefile + objHead + tTxt + dpTxt + ' End:\n\n'
        elif tStr != 'NA':
            placefile = placefile + objHead + tTxt + ' End:\n\n'
        elif dpStr != 'NA':
            placefile = placefile + objHead + dpTxt + ' End:\n\n'
                    
        if wgstStr != 'NA' and wdirStr != 'NA':
            wgstText = gustObj(wdirStr, int(wgstStr), 'wgst')
            wgstTxt = objHead + wgstText + ' End:\n\n'
            placefile = placefile + wgstTxt
        if visStr != 'NA':
            vsbyTxt = objHead + visTxt + ' End:\n\n'
            placefile = placefile + vsbyTxt
        if rtStr != 'NA':
            rtTxt = objHead + rtTxt + ' End:\n\n'
            placefile = placefile + rtTxt

        #tempTxt = tempHead + '  Threshold: 100\n' + dpTxt + ' End:\n\n'
        tempcsv = str(lon) + ',' + str(lat) + ',' + visStr + ',' + rtStr + '\n'
        #placefile = placefile + tempTxt

        if visStr == 'NA' and rtStr == 'NA':
            pass
        else:
            csvFile = csvFile + tempcsv

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
"""
TimeRange: 2019-03-06T23:14:39Z 2019-03-06T23:16:29Z

"""