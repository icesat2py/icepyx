#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 13:50:54 2020

@author: bissonk
"""

# made for Python 3.  It may work with Python 2.7, but has not been well tested

# libraries to call for all python API calls on Argovis

import requests
import pandas as pd
import os

#####
# Get current directory to save file into

curDir = os.getcwd()

# Get a selected region from Argovis 


def get_selection_profiles(startDate, endDate, shape, meas1,meas2, presRange=None):
    baseURL = 'https://argovis.colorado.edu/selection/bgc_data_selection'
    meas1Query = '?meas_1=' + meas1
    meas2Query = '&meas_2=' + meas2
    startDateQuery = '&startDate=' + startDate
    endDateQuery = '&endDate=' + endDate
    shapeQuery = '&shape='+shape
    if not presRange == None:
        pressRangeQuery = '&presRange=' + presRange
        url = baseURL + meas1Query + meas2Query + startDateQuery + endDateQuery + pressRangeQuery + '&bgcOnly=true' + shapeQuery
    else:
        url = baseURL + meas1Query + meas2Query + startDateQuery + endDateQuery + '&bgcOnly=true' + shapeQuery
    resp = requests.get(url)
    # Consider any status other than 2xx an error
    if not resp.status_code // 100 == 2:
        return "Error: Unexpected response {}".format(resp)
    selectionProfiles = resp.json()
    return selectionProfiles


def json2dataframe(selectionProfiles, measKey='measurements'):
    """ convert json data to Pandas DataFrame """
    # Make sure we deal with a list
    if isinstance(selectionProfiles, list):
        data = selectionProfiles
    else:
        data = [selectionProfiles]
    # Transform
    rows = []
    for profile in data:
        keys = [x for x in profile.keys() if x not in ['measurements', 'bgcMeas']]
        meta_row = dict((key, profile[key]) for key in keys)
        for row in profile[measKey]:
            row.update(meta_row)
            rows.append(row)
    df = pd.DataFrame(rows)
    return df
# set start date, end date, lat/lon coordinates for the shape of region and pres range

startDate='2020-10-08'
endDate='2020-10-22'
# shape should be nested array with lon, lat coords.
shape = '[[[-49.21875,48.806863],[-55.229808,54.85326],[-63.28125,60.500525],[-60.46875,64.396938],[-49.746094,61.185625],[-38.496094,54.059388],[-41.484375,47.754098],[-49.21875,48.806863]]]'
presRange='[0,30]'
meas1 = 'bbp700'
meas2 = 'chla'

meas1= 'temp'
meas2='psal'
# tested with  meas1 = temp, meas2 = psal and it works

selectionProfiles = get_selection_profiles(startDate, endDate, shape, meas1, meas2, presRange=None)


# loop thru profiles and search for measurement
tick1 = 0
tick2 = 0
for index, value in enumerate(selectionProfiles):
    if meas1 not in value['bgcMeasKeys']:
        tick1 += 1
    if meas2 not in value['bgcMeasKeys']:
        tick2 += 1  
if tick1 == len(selectionProfiles):
    print(f'{meas1} not found in selected data') 
if tick2 == len(selectionProfiles):
    print(f'{meas2} not found in selected data')     
                    
if tick1 < len(selectionProfiles) & tick2 < len(selectionProfiles):
    df = json2dataframe(selectionProfiles, measKey='bgcMeas')

df.head()

