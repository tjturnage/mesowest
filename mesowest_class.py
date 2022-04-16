
"""
05 Jan 2020: Now importing API_TOKEN for privacy since data are proprietary

Retrieves observations via the Mesowest API.
Learn more about setting up your own account at: https://synopticdata.com/

Getg latest obs: https://developers.synopticdata.com/mesonet/v2/stations/latest/
Obs network/station providers: https://developers.synopticdata.com/about/station-providers
Selecting stations: https://developers.synopticdata.com/mesonet/v2/station-selectors/

"""

import os
import sys

try:
    os.listdir('/usr')
    base_dir = '/home/tjt/public_html'
    sys.path.append('/data/scripts/resources')
    image_dir = os.path.join(base_dir,'placefiles')
except:
    windows = True
    sys.path.append('C:/data/scripts/resources')
    base_dir = 'C:/data'
    image_dir = os.path.join('C:/data','images')


import math
import requests
from datetime import datetime, timedelta
html_path = '/home/tjt/public_html'
public_path = os.path.join(html_path,'public')

from my_functions import timeShift
dstFile = '/home/tjt/public_html/public/placefiles/latest_surface_observations.txt'
#dstFile = 'latest_surface_observations.txt'

from api_tokens import mesowest_API_TOKEN as API_TOKEN
#API_TOKEN = 'token'  # placeholder for testing
API_ROOT = "https://api.synopticdata.com/v2/"
class Mesowest():
    """

    """

    def __init__(self,bbox="-91,39.5,-82,47.5",event_time=None):

        #self.states = states
        #self.radius_str=radius_str # "KLDM,100"
        self.bbox = bbox
        self.event_time = event_time
        self.dt = 5 # number of minutes to increment
        self.steps = 18 # number of increments
        self.network = "1,2,96"
        self.varStr = 'air_temp,dew_point_temperature,wind_speed,wind_direction,wind_gust,visibility'
        self.api_args = {"token":API_TOKEN,
                        "bbox":self.bbox, 
                        "status":"active",
                        "network":self.network,
                        "vars":self.varStr,
                        "units":"temp|F,speed|kts,precip|in",
                        "within":"30"}
    
        #print(self.api_args)

        if self.event_time is None:
            now = datetime.utcnow()
            self.baseTime = now - timedelta(minutes=now.minute%5) + timedelta(minutes=10)
            self.placeTime = now - timedelta(minutes=now.minute%5)
            self.place_ts = datetime.strftime(self.placeTime,'%Y%m%d%H%M')
        else:
            self.baseTime = datetime.strptime(self.event_time,'%Y%m%d%H%M')
            self.place_ts = self.event_time
        
        self.base_ts = datetime.strftime(self.baseTime,'%Y%m%d%H%M')
        print(self.base_ts)

        self.times = timeShift(self.base_ts,self.steps,self.dt,'backward','mesowest')

        self.shortDict = {'air_temp_value_1':'t',
                    'dew_point_temperature_value_1d':'dp',
                    'wind_speed_value_1':'wspd',
                    'wind_direction_value_1':'wdir',
                    'wind_gust_value_1':'wgst',
                    'visibility_value_1':'vis'}
        
        self.varList = list(self.shortDict.keys())
        self.wind_zoom = 500
        self.t_zoom = 300
        self.stnDict2 = {'t':{'threshold':self.t_zoom,'color':'200 100 100','position':'-17,13, 1,'},
                'dp':{'threshold':self.t_zoom,'color':'0 255 0','position':'-17,-13, 1,'},
                'wspd':{'threshold':self.wind_zoom,'color':'255 255 255','position':'NA'},
                'wdir':{'threshold':self.wind_zoom,'color':'255 255 255','position':'NA'},
                'wgst':{'threshold':self.wind_zoom,'color':'255 255 255','position':'NA'},
                'vis':{'threshold':100,'color':'180 180 255','position':'17,-13, 1,'},
                'rt':{'threshold':125,'color':'255 255 0','position':'17,13, 1,'}}

        self.placeTitle = f'Surface obs_{self.place_ts[0:4]}-{self.place_ts[4:6]}-{self.place_ts[6:8]}-{self.place_ts[-4:]}'  
        placeFileName = 'latest_surface_observations.txt'
        self.build_placefile();

    def str_to_fl(self,string):
        """
        Tries to convert string to float. If unsuccessful, returns 'NA' string
        """
        try:
            return float(string)
        except:
            return 'NA'

    def build_placefile(self):
        self.placefile = 'Title: Mesowest ' + self.placeTitle + '\nRefresh: 1\nColor: 255 200 255\n \
        IconFile: 1, 18, 32, 2, 31, "https://mesonet.agron.iastate.edu/request/grx/windbarbs.png" \n \
        IconFile: 2, 15, 15, 8, 8, "https://mesonet.agron.iastate.edu/request/grx/cloudcover.png"\n \
        IconFile: 3, 25, 25, 12, 12, "https://mesonet.agron.iastate.edu/request/grx/rwis_cr.png"\n \
        Font: 1, 14, 1, "Arial"\n\n'


        for t in range(0,len(self.times)):
            timeStr = self.times[t][0]
            jas = self.mesowest_get_nearest_time_data(timeStr)
            now = self.times[t][1]
            future = self.times[t][2]
            """
            TimeRange: 2019-03-06T23:14:39Z 2019-03-06T23:16:29Z
            """
            #timeText = 'TimeRange: ' + now + ' ' + future + '\n\n'
            timeText = f'TimeRange: {now} {future}\n\n'
            self.placefile += timeText                
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
                    for k in range(0,len(self.varList)):
                        thisVar = str(self.varList[k])
                        short = str(self.shortDict[thisVar])
                        try:
                            scratch = jas['STATION'][j]['OBSERVATIONS'][thisVar]['value']
                            if short == 't':
                                tStr, textInfo = self.convert_met_values(scratch,short)
                                tTxt = tempTxt + textInfo
                            elif short == 'dp':
                                dpStr, textInfo = self.convert_met_values(scratch,short)
                                dpTxt = tempTxt + textInfo
                            elif short == 'rt':
                                rtStr, textInfo = self.convert_met_values(scratch,short)
                                rtTxt = tempTxt + textInfo
                            elif short == 'vis':
                                visStr, textInfo = self.convert_met_values(scratch,short)
                                visTxt = tempTxt + textInfo
                            elif short == 'wspd':
                                wspdStr, val = self.convert_met_values(scratch,short)
                            elif short == 'wdir':
                                wdirStr, val = self.convert_met_values(scratch,short)                    
                            elif short == 'wgst':
                                wgstStr, textInfo = self.convert_met_values(scratch,short)
                                wgstTxt = tempTxt + textInfo                
                        except:
                            pass

                objHead = f'Object: {lat},{lon}\n'     

                if wdirStr != 'NA' and wspdStr != 'NA':
                    self.placefile += f'{objHead}  Threshold: {self.wind_zoom}\n  Icon: 0,0,{wdirStr},1,{wspdStr}\n End:\n\n'

                if tStr != 'NA' and dpStr != 'NA':
                    self.placefile += f'{objHead}{tTxt}{dpTxt} End:\n\n'
                elif tStr != 'NA':
                    self.placefile += f'{objHead}{tTxt} End:\n\n'
                elif dpStr != 'NA':
                    self.placefile += f'{objHead}{dpTxt} End:\n\n'
                            
                if wgstStr != 'NA' and wdirStr != 'NA':
                    wgstText = self.gustObj(wdirStr, int(wgstStr), 'wgst')
                    self.placefile += f'{objHead}{wgstText} End:\n\n'
                if visStr != 'NA':
                    self.placefile += f'{objHead}{visTxt} End:\n\n'
                if rtStr != 'NA':
                    self.placefile += f'{objHead}{rtTxt} End:\n\n'

        with open(dstFile, 'w') as outfile:
            outfile.write(self.placefile)

    def mesowest_get_nearest_time_data(self,timeStr):
        """
        Mesowest API request for data at the nearest available time defined by a time string.
        
        Parameters
        ----------
            timeStr : string
                      format is YYYYmmDDHHMM (ex. 202002290630)
        Returns
        -------
               code : json file
                      observational data
        """
        api_request_url = os.path.join(API_ROOT, "stations/nearesttime")
        self.api_args['attime'] = timeStr
        req = requests.get(api_request_url, params=self.api_args)
        jas = req.json()
        return jas

    def mesowest_get_latest_observations(self):
        """                 
        Returns
        -------
                jas2 : json file
                        Dictionary of metadata and observations for all stations within search area
            stns_list : list
                        list of ids of the stations that had data retrieved successfully
    
        """
        stns_list = []
        api_request_url = os.path.join(API_ROOT, "stations/latest")
        req = requests.get(api_request_url, params=self.api_args)
        jas2 = req.json()
        for s in range(0,len(jas2['STATION'])):
            try:
                station = jas2['STATION'][s]
                stn_id = station['STID']
                print(stn_id)
                stns_list.append(str(stn_id))
                lat = station['LATITUDE']
                lon = station['LONGITUDE']        
                ob_time = station['OBSERVATIONS']['wind_gust_value_1']['date_time']
                wgst = station['OBSERVATIONS']['wind_gust_value_1']['value']
                wdir = station['OBSERVATIONS']['wind_direction_value_1']['value']
                wspd = station['OBSERVATIONS']['wind_speed_value_1']['value']
                dwpt = station['OBSERVATIONS']['dew_point_temperature_value_1d']['value']
                temp = station['OBSERVATIONS']['air_temp_value_1']['value']
                print(stn_id)
                line = ([stn_id,ob_time,lat,lon,temp,dwpt,wdir,wspd,wgst])
                print(line)
            except:
                pass

        return jas2,stns_list

       
    def mesowest_get_timeseries(self,start_time,end_time,stns_list,dst_file):
        """
        For each station in a list of stations, retrieves all observational data within a defined
        time range using mesowest API. Writes the retrieved data and associated observation times
        to a destination file. API documentation:
        
            https://developers.synopticdata.com/mesonet/v2/stations/timeseries/
        
        Parameters
        ----------
            start_time : string 
                        data start time to be passed to the mesowest API
                        format - YYYYMMDDhhmm
                        
            end_time : string 
                        data end time to be passed to the mesowest API
                        format - YYYYMMDDhhmm
                
            stns_list : list
                        stations that will have time series data requested
                        This can either be a pre-staged list or can come from 
                        mesowest_get_current_observations function
                        
            dst_file : Path to file that will be written to with 
                        

                                            
        Returns
        -------
                jas_ts : json file
                        dictionary of all observations for a given station
                        
                        What is most significant, however, is writing the observed data
                        to a file that then can be manipulated for plotting
    
        """
        stns = ','.join(stns_list)
        with open(dst_file,'w') as fout:
        #stn_data = []
            #api_arguments = {"token":API_TOKEN,"stid":stns,"start":start_time ,"end":end_time ,"vars": varStr, "units": unitsStr}
            api_request_url = os.path.join(API_ROOT, "stations/timeseries")
            req = requests.get(api_request_url, params=self.api_args)
            jas_ts = req.json()
            for s in range(0,len(jas_ts['STATION'])):
                try:
                    station = jas_ts['STATION'][s]
                    stn_id = station['STID']
                    print(stn_id)
                    lat = station['LATITUDE']
                    lon = station['LONGITUDE']        
                    ob_times = station['OBSERVATIONS']['date_time']
                    print(ob_times)

                    wgsts = station['OBSERVATIONS']['wind_gust_set_1']
                    wdirs = station['OBSERVATIONS']['wind_direction_set_1']
                    wspds = station['OBSERVATIONS']['wind_speed_set_1']
                    dwpts = station['OBSERVATIONS']['dew_point_temperature_set_1d']
                    temps = station['OBSERVATIONS']['air_temp_set_1']
                    for dt in range(0,len(ob_times)):
                        line = ','.join([ob_times[dt][:-1],stn_id,lat,lon,str(temps[dt]),str(dwpts[dt]),str(wdirs[dt]),str(wspds[dt]),str(wgsts[dt])])
                        print(line)
                        fout.write(line + '\n')
                except:
                    pass
            return jas_ts

    def mesowest_data_from_dataframe(self,dataframe,pd_time,station):
        """
        Identifies the most recent observation in a dataframe sliced by time and station.
        Returns those values
        
        Parameters
        ----------
            dataframe : pandas dataframe from which a slice will be taken  
                pd_time : pandas datetime that's used to slice off all preceeding data
                station : string 
                        mesowest station id for which latest observation time will be determined
                                            
        Returns
        -------
            stn_data : list
                        extacts metadata and (t,dp,wdir,wspd,wgust) from latest observation using '.max()'
                        calls 'str_to_flt' function to convert number strings to floats
                        if (t,dp,wdir,wspd) all exist
                            returns list of data values associated with the observation
                        otherwise returns nothing

    
        """

        sfc_D = dataframe
        new_data = None
        try:
            new_data = sfc_D[(sfc_D.index < pd_time) & (sfc_D.station_id == station)]
            new_data_max = new_data[new_data.index == new_data.index.max()]
            index_time = pd_time.strftime('%Y%m%d%H%M')
            ob_time = new_data_max.index[0].strftime('%Y%m%d%H%M')
            lat = self.str_to_fl(new_data_max.lat.values[-1])
            lon = self.str_to_fl(new_data_max.lon.values[-1])
            t = self.str_to_fl(new_data_max.temp.values[-1])    
            dp = self.str_to_fl(new_data_max.dewpoint.values[-1])
            wdir = self.str_to_fl(new_data_max.wdir.values[-1])   
            wspd = self.str_to_fl(new_data_max.wspd.values[-1])
            wgst = self.str_to_fl(new_data_max.wgst.values[-1])
            #data_path = new_data.file_path.max()
            stn_data = [station,index_time,ob_time,lat,lon,t,dp,wdir,wspd,wgst]
            if 'NA' not in (t,dp,wdir,wspd):
                return stn_data
            else:
                return None
        except:
            return None


    def placefileWindSpeedCode(self,wspd):
        """
        Returns the proper code for plotting wind speeds in a GR2Analyst placefile. 
        This code is then used for the placefile IconFile method described at:
            http://www.grlevelx.com/manuals/gis/files_places.htm
        
        Parameters
        ----------
                wspd : string
                        wind speed in knots
                                            
        Returns
        -------
                code : string
                        string of integer to be used to reference placefile icon

        """
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
        
        
    def windDir(self,wdir):
        """
        Returns the proper code for plotting wind speeds in a GR2Analyst placefile. 
        This code is then used for the placefile IconFile method described at:
            http://www.grlevelx.com/manuals/gis/files_places.htm
        
        Parameters
        ----------
                wspd : string
                        wind speed in knots
                                            
        Returns
        -------
                code : string
                        string of integer to be used to reference placefile icon

        """

        wd = int(wdir)
        if wd < 20:
            wc = 'N'    
        elif wd < 75:
            wc = 'NE'
        elif wd < 115:
            wc = 'E'
        elif wd < 155:
            wc = 'SE'
        elif wd < 200:
            wc = 'S'
        elif wd < 250:
            wc = 'SW'
        elif wd < 290:
            wc ='W'
        elif wd < 340:
            wc = 'NW'
        else:
            wc = 'N'

        return wd,wc        


    def convert_met_values(self,num,short):
        numfloat = float(num)
        if (num != 'NA' ):
            if (short == 't') or (short == 'dp') or (short == 'rt'):
                new = int(round(numfloat))
                newStr = '" ' + str(new) + ' "'
                textInfo = self.buildObject(newStr,short)
            elif short == 'wgst':
                new = int(round(numfloat,1))
                newStr = '" ' + str(new) + ' "'        
                textInfo = self.buildObject(newStr,short)
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
                textInfo = self.buildObject(newStr,short)
            elif short == 'wspd':
                new = self.placefileWindSpeedCode(numfloat)
                newStr = str(new)
                textInfo = 'ignore'
            elif short == 'wdir':
                new = int(num)
                newStr = str(new)
                textInfo = 'ignore'

            return newStr, textInfo

    def gustObj(self,wdir, wgst, short):
        wgstInt = int(wgst)
        newStr = '" ' + str(wgstInt) + ' "'
        direction = int(wdir)
        distance = 35
        x = math.sin(math.radians(direction)) * distance
        y = math.cos(math.radians(direction)) * distance
        loc = str(int(x)) + ',' + str(int(y)) + ',1,'
        threshLine = 'Threshold: ' + str(self.stnDict2[short]['threshold']) + '\n'
        colorLine = '  Color: ' + str(self.stnDict2[short]['color']) + '\n'
        position = '  Text: ' + loc + newStr + ' \n'
        textInfo = threshLine + colorLine + position
        return textInfo

    def buildObject(self,newStr,short):
        threshLine = 'Threshold: ' + str(self.stnDict2[short]['threshold']) + '\n'
        colorLine = '  Color: ' + str(self.stnDict2[short]['color']) + '\n'
        position = '  Text: ' + str(self.stnDict2[short]['position']) + newStr + '\n'
        textInfo = threshLine + colorLine + position
        return textInfo




if __name__ == "__main__":
    test = Mesowest()