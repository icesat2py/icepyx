import requests # dependency for icepyx
import pandas as pd # dependency for icepyx? - geopandas
import os
from .dataset import *

class Argo_bgc(DataSet):

    def __init__(self, shape, timeframe, meas1, meas2, presRange=None):
        self.shape = shape
        self.bounding_box = shape.extent # call coord standardization method (see icepyx)
        self.time_frame = timeframe # call fmt_timerange
        self.meas1 = meas1
        self.meas2 = meas2
        self.presrng = presRange

    def download(self, out_path):
        baseURL = 'https://argovis.colorado.edu/selection/bgc_data_selection'
        meas1Query = '?meas_1=' + self.meas1
        meas2Query = '&meas_2=' + self.meas2
        startDateQuery = '&startDate=' + self.time_frame[0].strftime('%Y-%m-%d')
        endDateQuery = '&endDate=' + self.time_frame[1].strftime('%Y-%m-%d')

        shapeQuery = '&shape=' + self.shape # might have to process this
        if not self.presrng == None:
            pressRangeQuery = '&presRange=' + self.presrng
            url = baseURL + meas1Query + meas2Query + startDateQuery + endDateQuery + pressRangeQuery + '&bgcOnly=true' + shapeQuery
        else:
            url = baseURL + meas1Query + meas2Query + startDateQuery + endDateQuery + '&bgcOnly=true' + shapeQuery
        resp = requests.get(url)

        # Consider any status other than 2xx an error
        if not resp.status_code // 100 == 2:
            return "Error: Unexpected response {}".format(resp)
        selectionProfiles = resp.json()

        # save selection profiles somewhere
        # return selectionProfiles





