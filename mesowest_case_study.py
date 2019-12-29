#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 21:30:11 2019

@author: tj

"""

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
        new = datetime.strftime(newTime, '%Y-%m-%dT%H:%M:%S')
        nextTimeStr = datetime.strftime(nextTime, '%Y-%m-%dT%H:%M:%S')
        times.append([newStr,new,nextTimeStr])
    return times
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

import math
import requests
import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from datetime import datetime, timedelta,timezone 
from metpy.calc import reduce_point_density
from metpy.calc import wind_components
#from metpy.cbook import get_test_data
from metpy.plots import add_metpy_logo, current_weather, sky_cover, StationPlot, wx_code_map
from metpy.units import units
from gis_layers import shape_mini

from mesowest_functions import str_to_fl,mesowest_data_from_latest_observation
from mesowest_functions import mesowest_get_timeseries,mesowest_get_current_observations


from case_data import this_case
event_date = this_case['date']
rda = this_case['rda']
extent = this_case['sat_extent']
extent = [-88.4,-84.0,42.5,45.3]
orig_extent = extent
pd = this_case['pandas']
p_ts = pd[0]
p_steps = pd[1]
p_int = pd[2]
shapelist = this_case['shapelist']
case_dir = os.path.join(base_dir,event_date)

import pandas as pd
df = None

fout = 'C:/data/timeseries.txt'
df = pd.read_csv(fout, index_col='newTimeStr', 
                 names=['newTimeStr','time', 'station_id', 'lat', 'lon', 'temp', 'dewpoint','wdir','wspd','wgst'])

formatT = "%Y-%m-%dT%H:%M:%SZ"


shortDict = {'air_temp_value_1':'t',
             'dew_point_temperature_value_1d':'dp',
             'wind_speed_value_1':'wspd',
             'wind_direction_value_1':'wdir',
             'wind_gust_value_1':'wgst',
             'visibility_value_1':'vis'}


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
dstFile = 'C:/data/20190720-obs.txt'
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


obsDict = {}

fout = 'C:/data/timeseries.txt'
jas2,stns_list,line = mesowest_get_current_observations()
stns = ','.join(stns_list)
jas_ts = mesowest_get_timeseries('201907200000','201907201930',stns,fout)

import pandas as pd
sfc_D = None
sfc_D = pd.read_csv(fout, header=0, index_col=['time'],parse_dates=True,names=['time', 'station_id', 'lat', 'lon', 'temp', 'dewpoint','wdir','wspd','wgst'])

idx = None
idx = pd.date_range(p_ts, periods=p_steps, freq=p_int)
dt = idx[1] - idx[0]
#dt_sfc = dt * 6
orig = idx[0]
py_dt = orig.to_pydatetime()
orig_time = py_dt.replace(tzinfo=timezone.utc).timestamp()

proj = ccrs.LambertConformal(central_longitude=-87, central_latitude=43,
                             standard_parallels=[35])


for i in range(0,len(idx)):
    plot_list = []
    sfc_df = []
    for station in stns_list:
        stn_data = mesowest_data_from_latest_observation(sfc_D,idx[i],station)
        if stn_data is not None:
            plot_list.append(stn_data)

    sfc_df = pd.DataFrame(plot_list, columns = ['station','index_time','ob_time','lat','lon','temp',
                                                'dewpoint','wind_dir','wind_speed','wgst'])

    #sfc_df.dropna(inplace=True,subset=['temp','dewpoint','wind_dir', 'wind_speed'])
    point_locs = proj.transform_points(ccrs.PlateCarree(), sfc_D['lon'].values, sfc_D['lat'].values)
    u, v = wind_components((sfc_df['wind_speed'].values * units('m/s')).to('knots'),
                       sfc_df['wind_dir'].values * units.degree)


    plt.rcParams['savefig.dpi'] = 255

# Create the figure and an axes set to the projection.
    fig = plt.figure(figsize=(20, 10))
    add_metpy_logo(fig, 1080, 290, size='large')
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    extent = [-88.4,-84.0,42.5,45.3]
# Add some various map elements to the plot to make it recognizable.
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    for sh in shape_mini:
        ax.add_feature(shape_mini[sh], facecolor='none', edgecolor='gray', linewidth=0.5)
        ax.tick_params(axis='both', labelsize=8)

    stationplot = StationPlot(ax, sfc_df['lon'].values, sfc_df['lat'].values, clip_on=True,
                          transform=ccrs.PlateCarree(), fontsize=10)

    stationplot.plot_parameter('NW', sfc_df['temp'], color='red')
    stationplot.plot_parameter('SW', sfc_df['dewpoint'],
                           color='darkgreen')

    stationplot.plot_barb(u, v)

    plt.show()        