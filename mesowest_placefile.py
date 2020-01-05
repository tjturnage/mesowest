#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""


"""


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


from datetime import datetime
from mesowest_functions import convert_met_values,shortDict
from mesowest_functions import gustObj, mesowest_get_nearest_time_data
from my_functions import timeShift

formatT = "%Y-%m-%dT%H:%M:%SZ"

#varStr = 'visibility,road_temp'
varStr = 'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,visibility,road_temp'
unitsStr = 'temp|F,speed|kts,precip|in'

varList =[]
for keys in shortDict:
    varList.append(str(keys))


nowTime = datetime.utcnow()
nowTimeStr = datetime.strftime(nowTime,'%b %d,%Y %H:%M UTC')
nowTimeStr2 = datetime.strftime(nowTime,'%Y%m%d%H%M')

archive_timestr = '201907201800'
archive = True

if archive:
    timeStr = archive_timestr
else:
    timeStr = nowTimeStr2

dt = 30
niceTime = timeStr[0:4] + '-' + timeStr[4:6] + '-' + timeStr[6:8] + '-' + timeStr[-4:]  
num = 5
numMin = str(dt * num)
placeFileName = 'Surface obs_' + niceTime + '_' + numMin + 'minutes.txt'
placeTitle = 'Surface obs_' + niceTime + '_' + numMin + 'minutes'

direction = 'backward' # 'forward'
times = timeShift(timeStr,num,dt,direction)


placefile = 'Title: Mesowest ' + placeTitle + '\nRefresh: 2\nColor: 255 200 255\n \
IconFile: 1, 18, 32, 2, 31, "https://mesonet.agron.iastate.edu/request/grx/windbarbs.png" \n \
IconFile: 2, 15, 15, 8, 8, "https://mesonet.agron.iastate.edu/request/grx/cloudcover.png"\n \
IconFile: 3, 25, 25, 12, 12, "https://mesonet.agron.iastate.edu/request/grx/rwis_cr.png"\n \
Font: 1, 14, 1, "Arial"\n\n'


for t in range(0,len(times)):
    jas = mesowest_get_nearest_time_data(timeStr, archive)

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
                        tStr, textInfo = convert_met_values(scratch,short)
                        tTxt = tempTxt + textInfo
                    elif short == 'dp':
                        dpStr, textInfo = convert_met_values(scratch,short)
                        dpTxt = tempTxt + textInfo
                    elif short == 'rt':
                        rtStr, textInfo = convert_met_values(scratch,short)
                        rtTxt = tempTxt + textInfo
                    elif short == 'vis':
                        visStr, textInfo = convert_met_values(scratch,short)
                        visTxt = tempTxt + textInfo
                    elif short == 'wspd':
                        wspdStr, val = convert_met_values(scratch,short)
                    elif short == 'wdir':
                        wdirStr, val = convert_met_values(scratch,short)                    
                    elif short == 'wgst':
                        wgstStr, textInfo = convert_met_values(scratch,short)
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

try:
    os.chdir('C:/data/scripts/')
except:
    webDir = '/var/www/html/placefiles/'
else:
    webDir = 'C:/data/'

dstFile = os.path.join(image_dir,'placefiles',placeFileName)

with open(dstFile, 'w') as outfile:
    outfile.write(placefile)

"""
TimeRange: 2019-03-06T23:14:39Z 2019-03-06T23:16:29Z

"""