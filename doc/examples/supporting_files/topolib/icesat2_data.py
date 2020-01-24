import io
import json
import math
import pprint
import time
import zipfile
import os
import shutil
from statistics import mean
from xml.etree import ElementTree

import fiona

from topolib import EarthData

# To read KML files with geopandas, we will need to enable KML support
# in fiona (disabled by default)
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'


class IceSat2Data:
    PRODUCT_NAME = 'ATL06'

    NSIDC_URL = 'https://n5eil02u.ecs.nsidc.org'
    CAPABILITY_API = f'{NSIDC_URL}/egi/capabilities'
    DATA_REQUEST_URL = f'{NSIDC_URL}/egi/request'
    DOWNLOAD_URL = f'{NSIDC_URL}/esir/'

    REQUEST_HEADERS = {'Accept': 'application/json'}
    REQUEST_MODE = 'async'
    ORDER_PAGE_SIZE = 10

    EARTHDATA_URL = 'https://cmr.earthdata.nasa.gov'
    TOKEN_API_URL = f'{EARTHDATA_URL}/legacy-services/rest/tokens'
    CMR_COLLECTIONS_URL = f'{EARTHDATA_URL}/search/collections.json'
    GRANULE_SEARCH_URL = f'{EARTHDATA_URL}/search/granules'

    BEAMS = ['gt1r', 'gt1l', 'gt2r', 'gt2l', 'gt3r', 'gt3l']

    def __init__(self, user_id, password, **kwargs):
        """

        :param user_id: EarthData user ID
        :param password: EarthData password
        :param variables: dictionary with variables list for beams and other
                          supported ones.
                          Example:
                            {
                              'beams': '/land_ice_segments/h_li',
                              'other': '/orbit_info/cycle_number'
                            }
        :param kwargs: Optional:
                        'product' - Overwrite the default ATL06
        """
        self.session = EarthData(user_id, password)
        self.product_name = kwargs.get('product', self.PRODUCT_NAME)
        self._variables = kwargs.get('variables', None)
        self.product_version_id = self.latest_version_id()
        self.test_authentication()
        self._capabilities = None

    @property
    def capabilities(self):
        return self._capabilities

    @property
    def variables(self):
        return self._variables

    @variables.setter
    def variables(self, value):
        self._variables = value

    def test_authentication(self):
        """
        Check whether the given authentication combination is valid
        """
        if self.session.get(self.DATA_REQUEST_URL).status_code != 200:
            print('ERROR: Could not authorize with EarthData successfully')

    def latest_version_id(self):
        """
        Find most recent 'version_id' in metadata
        """
        response = self.session.get(
            self.CMR_COLLECTIONS_URL,
            params={'short_name': self.product_name}
        )
        response = json.loads(response.content)
        return max(
            [entry['version_id'] for entry in response['feed']['entry']]
        )

    @staticmethod
    def time_range_params(time_range):
        """
        Construct 'temporal' parameter for API call.

        :param time_range: dictionary with specific time range
                           *Required_keys* - 'start_date', 'end_date'
                           *Format* - 'yyyy-mm-dd'

        :return: Time string for request parameter or None if required keys are
                 missing.
        """
        start_time = '00:00:00'  # Start time in HH:mm:ss format
        end_time = '23:59:59'    # End time in HH:mm:ss format

        if 'start_date' not in time_range or 'end_date' not in time_range:
            return None

        return f"{time_range['start_date']}T{start_time}Z," \
            f"{time_range['end_date']}T{end_time}Z"

    @staticmethod
    def bounding_box_params(bounding_box):
        """
        Process a bounding box dictionary and returns a String as the NSIDC
        API expect the parameter.

        :param bounding_box:

        :return: String - for API parameter
        """
        return f"{bounding_box['LowerLeft_Lon']}," \
            f"{bounding_box['LowerLeft_Lat']}," \
            f"{bounding_box['UpperRight_Lon']}," \
            f"{bounding_box['UpperRight_Lat']}"

    def search_granules(self, **kwargs):
        """
        Search for granule with given dates and area.
        The area can be a bounding box for now.

        :param kwargs: 'bounding_box' as dictionary.
                       *Required keys* - 'LowerLeft_Lon', 'LowerLeft_Lat'
                                         'UpperRight_Lon', 'UpperRight_Lat'
                       'time_range': dictionary with specific time range
                       *Required_keys* - 'start_date', 'end_date'
                       *Format* - 'yyyy-mm-dd'

        :return:
        """

        if kwargs.get('bounding_box', None) is not None:
            params = {
                'short_name': self.product_name,
                'version': self.product_version_id,
                'page_size': 100,
                'page_num': 1,
                'bounding_box': self.bounding_box_params(
                    kwargs.get('bounding_box')
                ),
            }
        elif kwargs.get('polygon', None) is not None:
            # Polygon input (either via coordinate pairs or shapefile/KML/KMZ
            params = {
                'short_name': self.product_name,
                'version': self.product_version_id,
                'page_size': 100,
                'page_num': 1,
                'polygon': kwargs.get('polygon'),
            }
        else:
            print('Missing bounding box or polygon to search for')
            return -1

        time_range = self.time_range_params(kwargs.get('time_range', {}))
        if time_range is not None:
            params['temporal'] = time_range

        granules = []

        while True:
            response = self.session.get(
                self.GRANULE_SEARCH_URL,
                params=params,
                headers=self.REQUEST_HEADERS
            )

            results = json.loads(response.content)

            if len(results['feed']['entry']) == 0:
                # Out of results, so break out of loop
                break

            # Collect results and increment page_num
            granules.extend(results['feed']['entry'])
            params['page_num'] += 1

        if len(granules) > 0:
            granule_sizes = [float(granule['granule_size']) for granule in
                             granules]

            print('Number of granules:')
            print(f'    {len(granule_sizes)}')

            print('Average size of granules in MB:')
            print(f'    {mean(granule_sizes)}')
            print('Total size in MB:')
            print(f'    {sum(granule_sizes)}')

            return len(granule_sizes)
        else:
            return 0

    def variables_param(self):
        """
        Return the beam variables that will be requested via parameter
        :return: String
        """
        params = []

        if 'beams' in self.variables:
            params = params + [
                f'/{beam}{variable}' for variable in self.variables['beams']
                for beam in self.BEAMS
            ]

        if 'other' in self.variables:
            params = params + self.variables['other']

        return ','.join(params)

    def get_order_status(self, order_id):
        """
        Query the status API for given order.

        :param order_id

        :return: String of the order status
        """
        # Create status URL
        status_url = f'{self.DATA_REQUEST_URL}/{order_id}'
        # Find order status
        order_status_response = self.session.get(status_url)

        order_status_response.raise_for_status()
        root = ElementTree.fromstring(order_status_response.content)

        request_status = [
            status.text for status in root.findall("./requestStatus/")
        ]
        process_info = [
            info.text for info in root.findall("./processInfo/")
        ]

        return request_status[0], process_info

    def order_params(self, bounding_box, email, **kwargs):
        bounding_box = self.bounding_box_params(bounding_box)

        params = {
            'short_name': self.product_name,
            'version': self.product_version_id,
            'bounding_box': bounding_box,
            'bbox': bounding_box,
            'Coverage': self.variables_param(),
            'request_mode': self.REQUEST_MODE,
            'page_size': self.ORDER_PAGE_SIZE,
            'email': email,
        }

        time_range = self.time_range_params(kwargs.get('time_range', {}))
        if time_range is not None:
            params['temporal'] = time_range
            params['time'] = time_range.replace('Z', '')

        return params

    def order_data(
            self, email, destination_folder, bounding_box, **kwargs
    ):
        """
        Submit a data order to the NSIDC.

        :param email: Email address for notifications
        :param destination_folder:  Folder to download the data to
        :param bounding_box: Bounding box to constrain the search to
        :param kwargs: 'time_range': dictionary with specific time range
                                     *Required_keys* - 'start_date', 'end_date'
                                     *Format* - 'yyyy-mm-dd'
        """

        number_of_granules = self.search_granules(
            bounding_box=bounding_box, **kwargs
        )

        # Determine number of pages based on page_size and total granules.
        # Loop requests by this value
        page_num = math.ceil(number_of_granules / self.ORDER_PAGE_SIZE)

        params = self.order_params(bounding_box, email, **kwargs)

        # Request data service for each page number, and unzip outputs
        for i in range(page_num):
            page_val = i + 1
            print('Order: ', page_val)
            params.update({'page_num': page_val})

            # Post polygon to API endpoint for polygon subsetting to subset
            # based on original, non-simplified KML file
            # shape_post = {'shapefile': open(kml_filepath, 'rb')}
            # request = self.session.post(
            #   self.DATA_REQUEST_URL, params=params, files=shape_post
            # )

            # For all other requests that do not utilized an uploaded polygon
            # file, use a get request instead of post:
            request = self.session.get(
                self.DATA_REQUEST_URL, params=params
            )

            print('Request HTTP response: ', request.status_code)

            # Raise bad request: Loop will stop for bad response code.
            request.raise_for_status()

            response_root = ElementTree.fromstring(request.content)

            # Look up order ID
            orderlist = [
                order.text for order in response_root.findall("./order/")
            ]
            order_id = orderlist[0]
            print('order ID: ', order_id)

            status, messages = self.get_order_status(order_id)

            print('Data request ', page_val, ' is submitting...')
            print('Initial request status is ', status)

            messages = []
            # Continue to loop while request is still processing
            while status == 'pending' or status == 'processing':
                print('Status is not complete. Trying again.')
                time.sleep(10)

                status, messages = self.get_order_status(order_id)

                print('Retry request status is: ', status)
                if status == 'pending' or status == 'processing':
                    continue

            # Order can either complete, complete_with_errors, or fail:
            # Provide complete_with_errors error message:
            if (status == 'complete_with_errors' or status == 'failed') \
                    and len(messages) > 0:
                print('error messages:')
                pprint.pprint(messages)

            # Download zipped order if status is complete or
            # complete_with_errors
            if status == 'complete' or status == 'complete_with_errors':
                download_url = self.DOWNLOAD_URL + order_id + '.zip'

                print('Beginning download of zipped output...')
                zip_response = self.session.get(download_url)
                zip_response.raise_for_status()

                with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                    z.extractall(destination_folder)

                print('Data request', page_val, 'is complete.')
            else:
                print('Request failed.')
                
        self.clean_outputs(destination_folder)

    def get_capabilities(self):
        """
        Query service capability URL

        :return: Endpoint response parsed with ElementTree
        """
        if self.capabilities is None:
            capability_url = \
                f'{self.CAPABILITY_API}/' \
                f'{self.product_name}.{self.product_version_id}.xml'

            response = self.session.get(capability_url)
            self._capabilities = ElementTree.fromstring(response.content)

        return self.capabilities

    @staticmethod
    def convert_from_xml(variable):
        """
        Parse the value for a variable from the capabilities XML

        :param variable:
        :return: String of variable in order parameter format.
        """
        return list(filter(None, variable.attrib['value'].split(':')))

    def show_variables(self):
        """
        Query capabilities endpoint and show available variables
        """
        root = self.get_capabilities()

        all_variables = [
            self.convert_from_xml(variable)
            for variable in root.findall('.//SubsetVariable')
        ]

        variables = {'beams': [], 'other': []}

        for variable in all_variables:
            if variable[0] in self.BEAMS:
                variable = '/'.join(variable[1:])
                variables['beams'].append(variable)
            else:
                variables['other'].append('/'.join(variable))

        variables['beams'] = sorted(list(set(variables['beams'])))
        variables['other'] = sorted(list(set(variables['other'])))

        pprint.pprint(variables)

    def show_formats(self):
        """
        Query capabilities endpoint and show available download formats
        """
        root = self.get_capabilities()

        formats = [
            variable.attrib['value'] for variable in root.findall('.//Format')
        ]
        formats.remove('')
        formats.append('No reformatting')

        pprint.pprint(formats)

    def show_projections(self):
        """
        Query capabilities endpoint and show available data projections
        *NOTE*: Not yet supported
        """
        root = self.get_capabilities()

        projections = root.find('.//Projections').attrib['normalProj'].split(',')
        projections.remove('')
        projections.append('No change')

        print('WARNING - Currently not available')
        print('  Only applicable on ICESat-2 L3B products')
        pprint.pprint(projections)
        
    def clean_outputs(self, destination_folder):
        #Clean up Outputs folder by removing individual granule folders 
        for root, dirs, files in os.walk(destination_folder, topdown=False):
            for file in files:
                try:
                    shutil.move(os.path.join(root, file), destination_folder)
                except OSError:
                    pass
            for name in dirs:
                os.rmdir(os.path.join(root, name))
