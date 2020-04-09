import requests
import time
import io
import json
import numpy as np
import pprint
from xml.etree import ElementTree as ET
import zipfile

import icepyx.core.APIformatting as apifmt

def info(grans):
    """
    Return some basic information about a set of granules for an 
    ICESat-2 data object. Granule info may be from a list of those available
    from NSIDC (for ordering/download) or a list of granules present on the
    file system.

    Examples
    --------
    >>>
    """
    assert len(grans)>0, "Your data object has no granules associated with it"
    gran_info = {}
    gran_info.update({'Number of available granules': len(grans)})

    gran_sizes = [float(gran['granule_size']) for gran in grans]
    gran_info.update({'Average size of granules (MB)': np.mean(gran_sizes)})
    gran_info.update({'Total size of all granules (MB)': sum(gran_sizes)})

    return gran_info


#DevGoal: this will be a great way/place to manage data from the local file system
#where the user already has downloaded data!
class Granules():
    """
    Interact with ICESat-2 data granules. This includes finding,
    ordering, and downloading them as well as (not yet implemented) getting already
    downloaded granules into the ICESat-2 data object.

    Parameters
    ----------
    avail : dict?
        Earthdata Login user name (user ID).
    orderIDs : list of strings

    files : list of filename strings

    session : need to put here?


    Returns
    -------
    Granules object

    Examples
    --------
    >>> example
    result
    """
        
    def __init__(
        self,
        avail=[],
        orderIDs=[],
        files=[],
        session=None
    ):

        self.avail = avail
        self.orderIDs = orderIDs
        self.files = files
        self._session = session

        # assert isinstance(uid, str), "Enter your login user id as a string"
        # assert re.match(r'[^@]+@[^@]+\.[^@]+',email), "Enter a properly formatted email address"

        print(self._session)
    # ----------------------------------------------------------------------
    # Methods

    def get_avail(self,CMRparams,reqparams):
        """
        Get a list of available granules for the ICESat-2 data object's parameters
        """

        assert CMRparams is not None and reqparams is not None, "Missing required input parameter dictionaries"

        granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'

        headers={'Accept': 'application/json'}
        #DevGoal: check the below request/response for errors and show them if they're there; then gather the results
        #note we should also do this whenever we ping NSIDC-API - make a function to check for errors
        while True:
            response = requests.get(granule_search_url, headers=headers,\
                                    params=apifmt.combine_params(CMRparams,\
                                                               {k: reqparams[k] for k in ('page_size','page_num')}))

            results = json.loads(response.content)

            if len(results['feed']['entry']) == 0:
                # Out of results, so break out of loop
                break

            # Collect results and increment page_num
            self.avail.extend(results['feed']['entry'])
            reqparams['page_num'] += 1

        assert len(self.avail)>0, "Your search returned no results; try different search parameters"

    
    def place_order(self, CMRparams, reqparams, subsetparams, verbose, subset, **kwargs):
        """
        Place an order for the available granules for the ICESat-2 data object.
        Adds the list of zipped files (orders) to the data object.
        DevGoal: add additional kwargs to allow subsetting and more control over request options.
        Note: This currently uses paging to download data - this may not be the best method

        Parameters
        ----------
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object can be obtained using is2_data.earthdata_login(uid, email) and entering your
            Earthdata login password when prompted. You must have previously registered for an Earthdata account.

        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.

        subset : boolean, default True
            Use input temporal and spatial search parameters to subset each granule and return only data
            that is actually within those parameters (rather than complete granules which may contain only
            a small area of interest).

        kwargs...
        """

        if self._session is None:
           raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")

        base_url = 'https://n5eil02u.ecs.nsidc.org/egi/request'
        #DevGoal: get the base_url from the granules?

        if subset is False:
            request_params = apifmt.combine_params(CMRparams, reqparams, {'agent':'NO'})
        else:
            request_params = apifmt.combine_params(CMRparams, reqparams, subsetparams)

        granules=self.get_avail(CMRparams, reqparams) #this way the reqparams['page_num'] is updated

        # Request data service for each page number, and unzip outputs
        for i in range(request_params['page_num']):
            page_val = i + 1
            if verbose is True:
                print('Order: ', page_val)
            request_params.update( {'page_num': page_val} )

        #REFACTOR: this is going to break now when a polygon is tried!!!
        # For all requests other than spatial file upload, use get function
        #add line here for using post instead of get with polygon and subset
        #also, make sure to use the full polygon, not the simplified one used for finding granules
            if subset is True and hasattr(self, '_geom_filepath'):
                #post polygon file to OGR for geojson conversion
                #DevGoal: what is this doing under the hood, and can we do it locally?

                request = self._session.post(base_url, params=request_params, \
                                       files={'shapefile': open(str(self._geom_filepath), 'rb')})
            else:
                request = self._session.get(base_url, params=request_params)
            
            root=ET.fromstring(request.content)
            print([subset_agent.attrib for subset_agent in root.iter('SubsetAgent')])

            if verbose is True:
                print('Request HTTP response: ', request.status_code)
                print('Order request URL: ', request.url)

        # Raise bad request: Loop will stop for bad response code.
            request.raise_for_status()
            esir_root = ET.fromstring(request.content)
            if verbose is True:
                print('Order request URL: ', request.url)
                print('Order request response XML content: ', request.content)

        #Look up order ID
            orderlist = []
            for order in esir_root.findall("./order/"):
                if verbose is True:
                    print(order)
                orderlist.append(order.text)
            orderID = orderlist[0]
            print('order ID: ', orderID)

        #Create status URL
            statusURL = base_url + '/' + orderID
            if verbose is True:
                print('status URL: ', statusURL)

        #Find order status
            request_response = self._session.get(statusURL)
            if verbose is True:
                print('HTTP response from order response URL: ', request_response.status_code)

        # Raise bad request: Loop will stop for bad response code.
            request_response.raise_for_status()
            request_root = ET.fromstring(request_response.content)
            statuslist = []
            for status in request_root.findall("./requestStatus/"):
                statuslist.append(status.text)
            status = statuslist[0]
            print('Data request ', page_val, ' is submitting...')
            print('Initial request status is ', status)

        #Continue loop while request is still processing
            while status == 'pending' or status == 'processing':
                print('Status is not complete. Trying again.')
                time.sleep(10)
                loop_response = self._session.get(statusURL)

        # Raise bad request: Loop will stop for bad response code.
                loop_response.raise_for_status()
                loop_root = ET.fromstring(loop_response.content)

        #find status
                statuslist = []
                for status in loop_root.findall("./requestStatus/"):
                    statuslist.append(status.text)
                status = statuslist[0]
                print('Retry request status is: ', status)
                if status == 'pending' or status == 'processing':
                    continue

        #Order can either complete, complete_with_errors, or fail:
        # Provide complete_with_errors error message:
            if status == 'complete_with_errors' or status == 'failed':
                messagelist = []
                for message in loop_root.findall("./processInfo/"):
                    messagelist.append(message.text)
                print('error messages:')
                pprint.pprint(messagelist)

            if status == 'complete' or status == 'complete_with_errors':
                if not hasattr(self,'orderIDs'):
                    self.orderIDs=[]

                self.orderIDs.append(orderID)
            else: print('Request failed.')

        return self.orderIDs

    
    def download(self, verbose, path):
        """
        Downloads the data ordered using order_granules.

        Parameters
        ----------
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object can be obtained using is2_data.earthdata_login(uid, email) and entering your
            Earthdata login password when prompted. You must have previously registered for an Earthdata account.
        verbose : boolean, default False
            Print out all feedback available from the download process.
            Progress information is automatically printed regardless of the value of verbose.
        """
        """
        extract : boolean, default False
            Unzip the downloaded granules.
        """

        #Note: need to test these checks still
        if self._session is None:
            raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")
            #DevGoal: make this a more robust check for an active session

        if not hasattr(self,'orderIDs') or len(self.orderIDs)==0:
            try:
                self.place_order(verbose=verbose)
            except:
                if not hasattr(self,'orderIDs') or len(self.orderIDs)==0:
                    raise ValueError('Please confirm that you have submitted a valid order and it has successfully completed.')

        for order in self.orderIDs:
            downloadURL = 'https://n5eil02u.ecs.nsidc.org/esir/' + order + '.zip'
            #DevGoal: get the download_url from the granules

 
            if verbose is True:
                print('Zip download URL: ', downloadURL)
            print('Beginning download of zipped output...')
            zip_response = self._session.get(downloadURL)
            # Raise bad request: Loop will stop for bad response code.
            zip_response.raise_for_status()
            print('Data request', order, 'of ', len(self.orderIDs), ' order(s) is complete.')

        #DevGoal: move this option back out to the is2class level and implement it in an alternate way?
        #         #Note: extract the dataset to save it locally
        # if extract is True:    
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                z.extractall(path)

