#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 20 21:30:11 2019

@author: tj

"""
"""
def station_plot(df):
    stationplot = StationPlot(ax, df['lon'].values, df['lat'].values, clip_on=True,
                          transform=ccrs.PlateCarree(), fontsize=10)

    stationplot.plot_parameter('NW', df['temp'], color='red')
    stationplot.plot_parameter('SW', df['dewpoint'], color='darkgreen')
    sfc_df = pd.DataFrame(plot_list, columns = ['station','index_time','ob_time','lat','lon','temp',
                                                'dewpoint','wind_dir','wind_speed','wgst'])

    #sfc_df.dropna(inplace=True,subset=['temp','dewpoint','wind_dir', 'wind_speed'])
    point_locs = proj.transform_points(ccrs.PlateCarree(), sfc_D['lon'].values, sfc_D['lat'].values)
    u, v = wind_components((sfc_df['wind_speed'].values * units('m/s')).to('knots'),
                       sfc_df['wind_dir'].values * units.degree)

"""
import os
import sys


try:
    os.listdir('/usr')
    windows = False
    sys.path.append('/data/scripts/resources')
except:
    sys.path.append('C:/data/scripts/resources')

from reference_data import set_paths

data_dir,image_dir,archive_dir,gis_dir,py_call,placefile_dir = set_paths()


import numpy as np
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from datetime import timezone,timedelta
from metpy.calc import wind_components

#from metpy.cbook import get_test_data
from metpy.plots import StationPlot
#from metpy.plots import add_metpy_logo, current_weather, sky_cover, wx_code_map
from metpy.units import units
from gis_layers import shape_mini


from mesowest_functions import mesowest_data_from_latest_observation
from mesowest_functions import mesowest_get_timeseries,mesowest_get_current_observations


from case_data import this_case
event_date = this_case['date']
case_dir = os.path.join(data_dir,event_date)
image_dir = os.path.join(case_dir,'surface')
os.makedirs(image_dir, exist_ok = True)
rda = this_case['rda']
try:
    extent = this_case['sat_extent']
except:
    extent = [-88.4,-84.0,42.5,45.3]
orig_extent = extent

shapelist = this_case['shapelist']


shortDict = {'air_temp_value_1':'t',
             'dew_point_temperature_value_1d':'dp',
             'wind_speed_value_1':'wspd',
             'wind_direction_value_1':'wdir',
             'wind_gust_value_1':'wgst',
             'visibility_value_1':'vis'}

# Build list of variable names from shortDict
varList =[]
for keys in shortDict:
    varList.append(str(keys))


# ---------------------------------------------------------
#                Station list section
# ---------------------------------------------------------
create_new_stations_list = True

stations_list = ['KACB','KAMN','KBIV','KCAD','KETB','KGOV','KGRB','KGRR','KHTL',
             'KLDM','KMBL','KMKG','KMOP','KMTW','KRQB','KSBM','KSUE','KTVC',
             'BDWM4','SBDM4','BDLM4','GYGM4','LEOM4','EVAM4','WLLM4','KFKS',
             '45007','MKGM4','MLWW3','SGNW3','KFFX','KY70','NMIM4','KOCQ','RSCM4','K3D2']

if create_new_stations_list: 
    jas2,stations_list = mesowest_get_current_observations("KDSM,100")

stns = ','.join(stations_list)


# ---------------------------------------------------------
#                Time series data section
# ---------------------------------------------------------
request_new_timeseries_data = True

import pandas as pd

# retrieve pandas time series information for the case
p = this_case['pandas']
p_ts = p[0]                 # initial time
p_steps = p[1]              # number of steps
p_int = p[2]                # time interval

# initialize pandas date range
idx = None
idx = pd.date_range(p_ts, periods=p_steps, freq=p_int)

# create time strings of start and end times to pass as
# agruments for requesting time series data from mesowest
start_time_pd = idx[0]
mesowest_start_time_pd = idx[0] - pd.Timedelta('1 hours')
end_time_pd = idx[-1]
start_time = start_time_pd.strftime('%Y%m%d%H%M')
mesowest_start_time = mesowest_start_time_pd.strftime('%Y%m%d%H%M')
end_time = end_time_pd.strftime('%Y%m%d%H%M')

py_dt = start_time_pd.to_pydatetime()
orig_time = py_dt.replace(tzinfo=timezone.utc).timestamp()

ts_file = 'C:/data/timeseries.txt'

if request_new_timeseries_data:
    mesowest_get_timeseries(mesowest_start_time,end_time,stations_list,ts_file)

# create pandas dataframe for time series data
sfc_D = None
sfc_D = pd.read_csv(ts_file, header=0, index_col=['time'],parse_dates=True,
                    names=['time', 'station_id', 'lat', 'lon', 'temp',
                           'dewpoint','wdir','wspd','wgst']) 

   
# ---------------------------------------------------------
#                Radar data section
# ---------------------------------------------------------

# Create list of radar files, their filepaths, and their valid times

from my_functions import make_radar_array, add_radar_paths, figure_timestamp


met_info = []
radar_dir = os.path.join(case_dir,rda,'netcdf/ReflectivityQC/00.50')
add_radar_paths(radar_dir,'.','r',met_info)

# make a dataframe of radar file paths using valid times as index
np_met_info = np.array(met_info)
metdat_D = pd.DataFrame(data=np_met_info[1:,1:],index=np_met_info[1:,0])  # 1st row as the column names
metdat_D.columns = ['data_type', 'file_path']

# ---------------------------------------------------------
#                Radar data section
# ---------------------------------------------------------
from custom_cmaps import plts
from my_functions import latest_file



for i in range(0,len(idx)):
    new_datetime = idx[i]

    fig_title,fig_fname_tstr = figure_timestamp(py_dt)

    plt.rcParams['savefig.dpi'] = 255

# Create the figure and an axes set to the projection.
    #fig = plt.figure(figsize=(20, 10))
    rows = 1
    cols = 1
    figure_size =(8,6)
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(rows,cols,figsize=figure_size,subplot_kw={'projection': ccrs.PlateCarree()})

    #add_metpy_logo(fig, 1080, 290, size='large')


    extent = [-88.0,-84.2,43.0,45.3]
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    for sh in shape_mini:
        ax.add_feature(shape_mini[sh], facecolor='none', edgecolor='gray', linewidth=0.5)
        ax.tick_params(axis='both', labelsize=8)

    radar_file = latest_file(metdat_D,new_datetime,'r')
    ra_filled,rlats,rlons = make_radar_array(radar_file,'Ref')
    cs = ax.pcolormesh(rlats,rlons,ra_filled,cmap=plts['Ref']['cmap'],vmin=plts['Ref']['vmn'], vmax=plts['Ref']['vmx'])
    #ax.pcolormesh(rlats,rlons,ra_filled,cmap=plts['Ref']['cmap'],vmin=plts['Ref']['vmn'], vmax=plts['Ref']['vmx'])

    plot_surface_observations = True
    if plot_surface_observations:
        plot_list = []
        for station in stations_list:
            stn_data = mesowest_data_from_latest_observation(sfc_D,idx[i],station)
            if stn_data is not None:
                plot_list.append(stn_data)
    
        sfc_df = None
        sfc_df = pd.DataFrame(plot_list, columns = ['station','index_time','ob_time','lat','lon','temp',
                                                    'dewpoint','wind_dir','wind_speed','wgst'])
    
        point_locs = proj.transform_points(ccrs.PlateCarree(), sfc_D['lon'].values, sfc_D['lat'].values)
        #u, v = wind_components((sfc_df['wind_speed'].values * units('m/s')).to('knots'),
        #                   sfc_df['wind_dir'].values * units.degree)
        u, v = wind_components((sfc_df['wind_speed'].values * units('knots')),sfc_df['wind_dir'].values * units.degree)
    
        stationplot = StationPlot(ax, sfc_df['lon'].values, sfc_df['lat'].values, clip_on=True,
                              transform=ccrs.PlateCarree(), fontsize=10)
    
        stationplot.plot_parameter('NW', sfc_df['temp'], color='#EE0000')
        stationplot.plot_parameter('SW', sfc_df['dewpoint'],
                               color='#009900')
    
        stationplot.plot_barb(u, v)

    cs = ax.pcolormesh(rlats,rlons,ra_filled,cmap=plts['Ref']['cmap'],vmin=plts['Ref']['vmn'], vmax=plts['Ref']['vmx'])
    

    stationplot.plot_barb(u, v)

    fig_fname = 'sfc_obs_' + idx[i].strftime('%Y%m%d_%H%M') + '.png'
    print(fig_fname)
    image_dst_path = os.path.join(image_dir,fig_fname)
    #plt.tight_layout()


    plot_title = 'Surface Observations - ' + idx[i].strftime('%d %b %Y %H%M UTC')
    ax.set_title(plot_title)
    plt.savefig(image_dst_path,format='png')
    plt.show()
    plt.close()