import requests
import time
import io
import json
import numpy as np
import os
import pprint
from xml.etree import ElementTree as ET
import zipfile

import icepyx.core.APIformatting as apifmt

def info(grans):
    """
    Return some basic summary information about a set of granules for an 
    icesat2data object. Granule info may be from a list of those available
    from NSIDC (for ordering/download) or a list of granules present on the
    file system.
    """
    assert len(grans)>0, "Your data object has no granules associated with it"
    gran_info = {}
    gran_info.update({'Number of available granules': len(grans)})

    gran_sizes = [float(gran['granule_size']) for gran in grans]
    gran_info.update({'Average size of granules (MB)': np.mean(gran_sizes)})
    gran_info.update({'Total size of all granules (MB)': sum(gran_sizes)})

    return gran_info

#DevNote: currently this fn is not tested
def gran_IDs(grans):
    """
    Returns a list of the granule IDs for the granule dictionary.
    Granule info may be from a list of those available from NSIDC (for ordering/download)
    or a list of granules present on the file system.
    """
    assert len(grans)>0, "Your data object has no granules associated with it"
    gran_ids = []
    for gran in grans:
        gran_ids.append(gran['producer_granule_id']) 
    
    return gran_ids


#DevGoal: this will be a great way/place to manage data from the local file system
#where the user already has downloaded data!
#DevNote: currently this class is not tested
class Granules():
    """
    Interact with ICESat-2 data granules. This includes finding,
    ordering, and downloading them as well as (not yet implemented) getting already
    downloaded granules into the icesat2data object.

    Returns
    -------
    Granules object
    """
        
    def __init__(
        self,
        # avail=[],
        # orderIDs=[],
        # files=[],
        # session=None
    ):
        pass
        # self.avail = avail
        # self.orderIDs = orderIDs
        # self.files = files
        # session = session
    
    # ----------------------------------------------------------------------
    # Methods

    def get_avail(self, CMRparams, reqparams):
        """
        Get a list of available granules for the icesat2data object's parameters.
        Generates the `avail` attribute of the granules object.

        Parameters
        ----------
        CMRparams : dictionary
            Dictionary of properly formatted CMR search parameters.
        reqparams : dictionary
            Dictionary of properly formatted parameters required for searching, ordering,
            or downloading from NSIDC.

        Notes
        -----
        This function is used by icesat2data.Icesat2Data.avail_granules(), which automatically
        feeds in the required parameters.
        
        See Also
        --------
        APIformatting.Parameters
        icesat2data.Icesat2Data.avail_granules
        """

        assert CMRparams is not None and reqparams is not None, "Missing required input parameter dictionaries"

        # if not hasattr(self, 'avail'): 
        self.avail=[]

        granule_search_url = 'https://cmr.earthdata.nasa.gov/search/granules'

        headers={'Accept': 'application/json'}
        #DevGoal: check the below request/response for errors and show them if they're there; then gather the results
        #note we should also do this whenever we ping NSIDC-API - make a function to check for errors
        while True:
            response = requests.get(granule_search_url, headers=headers,\
                                    params=apifmt.combine_params(CMRparams,\
                                                               {k: reqparams[k] for k in ('page_size','page_num')}))

            results = json.loads(response.content)

            # print(results)
            
            if len(results['feed']['entry']) == 0:
                # Out of results, so break out of loop
                break

            # Collect results and increment page_num
            self.avail.extend(results['feed']['entry'])
            reqparams['page_num'] += 1

        #DevNote: The above calculated page_num is wrong when mod(granule number, page_size)=0. 
        # print(reqparams['page_num'])
        reqparams['page_num'] = int(np.ceil(len(self.avail)/reqparams['page_size']))
    
        assert len(self.avail)>0, "Your search returned no results; try different search parameters"

    
    #DevNote: currently, default subsetting DOES NOT include variable subsetting, only spatial and temporal
    #DevGoal: add kwargs to allow subsetting and more control over request options.
    def place_order(self, CMRparams, reqparams, subsetparams, verbose, 
                    subset=True, session=None, geom_filepath=None): #, **kwargs):
        """
        Place an order for the available granules for the icesat2data object.
        Adds the list of zipped files (orders) to the granules data object (which is
        stored as the `granules` attribute of the icesat2data object).
        You must be logged in to Earthdata to use this function.

        Parameters
        ----------
        CMRparams : dictionary
            Dictionary of properly formatted CMR search parameters.
        reqparams : dictionary
            Dictionary of properly formatted parameters required for searching, ordering,
            or downloading from NSIDC.
        subsetparams : dictionary
            Dictionary of properly formatted subsetting parameters. An empty dictionary
            is passed as input here when subsetting is set to False in icesat2data methods.
        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.
        subset : boolean, default True
            Apply subsetting to the data order from the NSIDC, returning only data that meets the
            subset parameters. Spatial and temporal subsetting based on the input parameters happens
            by default when subset=True, but additional subsetting options are available.
            Spatial subsetting returns all data that are within the area of interest (but not complete
            granules. This eliminates false-positive granules returned by the metadata-level search)
        session : requests.session object
            A session object authenticating the user to order data using their Earthdata login information.
            The session object will automatically be passed from the icesat2data object if you
            have successfully logged in there.
        geom_filepath : string, default None
            String of the full filename and path when the spatial input is a file.
        
        Notes
        -----
        This function is used by icesat2data.Icesat2Data.order_granules(), which automatically
        feeds in the required parameters.
        
        See Also
        --------
        icesat2data.Icesat2Data.order_granules
        """

        if session is None:
           raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")

        base_url = 'https://n5eil02u.ecs.nsidc.org/egi/request'
        #DevGoal: get the base_url from the granules?


        self.get_avail(CMRparams, reqparams) #this way the reqparams['page_num'] is updated

        if subset is False:
            request_params = apifmt.combine_params(CMRparams, reqparams, {'agent':'NO'})
        else:
            request_params = apifmt.combine_params(CMRparams, reqparams, subsetparams)        
        
        order_fn = '.order_restart'
        
        print('Total number of data order requests is ',request_params['page_num'], ' for ',len(self.avail), ' granules.')
        #DevNote/05/27/20/: Their page_num values are the same, but use the combined version anyway.
        #I'm switching back to reqparams, because that value is not changed by the for loop. I shouldn't cause an issue either way, but I've had issues with mutable types in for loops elsewhere.
        for i in range(reqparams['page_num']):
#         for i in range(request_params['page_num']):
            page_val = i + 1
            
            print('Data request ', page_val, ' of ', reqparams['page_num'],' is submitting to NSIDC')
            request_params.update( {'page_num': page_val} )

            #DevNote: earlier versions of the code used a file upload+post rather than putting the geometries
            #into the parameter dictionaries. However, this wasn't working with shapefiles, but this more general
            #solution does, so the geospatial parameters are included in the parameter dictionaries.
            request = session.get(base_url, params=request_params)
            
            #DevGoal: use the request response/number to do some error handling/give the user better messaging for failures
            # print(request.content)
            root=ET.fromstring(request.content)
            #print([subset_agent.attrib for subset_agent in root.iter('SubsetAgent')])

            if verbose is True:
                print('Request HTTP response: ', request.status_code)
                # print('Order request URL: ', request.url)

        # Raise bad request: Loop will stop for bad response code.
            request.raise_for_status()
            esir_root = ET.fromstring(request.content)
            if verbose is True:
                print('Order request URL: ', request.url)
                print('Order request response XML content: ', request.content)

        #Look up order ID
            orderlist = []
            for order in esir_root.findall("./order/"):
                # if verbose is True:
                #     print(order)
                orderlist.append(order.text)
            orderID = orderlist[0]
            print('order ID: ', orderID)

        #Create status URL
            statusURL = base_url + '/' + orderID
            if verbose is True:
                print('status URL: ', statusURL)

        #Find order status
            request_response = session.get(statusURL)
            if verbose is True:
                print('HTTP response from order response URL: ', request_response.status_code)

        # Raise bad request: Loop will stop for bad response code.
            request_response.raise_for_status()
            request_root = ET.fromstring(request_response.content)
            statuslist = []
            for status in request_root.findall("./requestStatus/"):
                statuslist.append(status.text)
            status = statuslist[0]
            print('Initial status of your order request at NSIDC is: ', status)

        #Continue loop while request is still processing
            while status == 'pending' or status == 'processing':
                print('Your order status is still ', status, ' at NSIDC. Please continue waiting... this may take a few moments.')
                # print('Status is not complete. Trying again')
                time.sleep(10)
                loop_response = session.get(statusURL)

        # Raise bad request: Loop will stop for bad response code.
                loop_response.raise_for_status()
                loop_root = ET.fromstring(loop_response.content)

        #find status
                statuslist = []
                for status in loop_root.findall("./requestStatus/"):
                    statuslist.append(status.text)
                status = statuslist[0]
                # print('Retry request status is: ', status)
                if status == 'pending' or status == 'processing':
                    continue

        #Order can either complete, complete_with_errors, or fail:
        # Provide complete_with_errors error message:
            if status == 'complete_with_errors' or status == 'failed':
                messagelist = []
                for message in loop_root.findall("./processInfo/"):
                    messagelist.append(message.text)
                print('Your order is: ', status)
                print('NSIDC provided these error messages:')
                pprint.pprint(messagelist)

            if status == 'complete' or status == 'complete_with_errors':
                print('Your order is:', status)
                if not hasattr(self,'orderIDs'):
                    self.orderIDs=[]

                self.orderIDs.append(orderID)
            else: print('Request failed.')
        
        #DevGoal: save orderIDs more frequently than just at the end for large orders (e.g. for len(reqparams['page_num']) > 5 or 10 or something)
        #Save orderIDs to file to avoid resubmitting order in case kernel breaks down.
            # save orderIDs for every 5 orders when more than 10 orders are submitted. 
            # DevNote: These numbers are hard coded for now. Consider to allow user to set them in future?
            if reqparams['page_num']>=10 and i%5==0:
                with open(order_fn,'w') as fid:
                    json.dump({'orderIDs':self.orderIDs},fid)
                    
        # --- Output the final orderIDs            
        with open(order_fn,'w') as fid:
            json.dump({'orderIDs':self.orderIDs},fid)



        return self.orderIDs

    
    def download(self, verbose, path, session=None, restart=False):
        """
        Downloads the data for the object's orderIDs, which are generated by ordering data
        from the NSIDC.

        Parameters
        ----------
        verbose : boolean, default False
            Print out all feedback available from the order process.
            Progress information is automatically printed regardless of the value of verbose.
        path : string
            String with complete path to desired download directory and location.
        session : requests.session object
            A session object authenticating the user to download data using their Earthdata login information.
            The session object will automatically be passed from the icesat2data object if you
            have successfully logged in there.
        restart : boolean, default False
            Restart your download if it has been interrupted. If the kernel has been restarted, but you successfully
            completed your order, you will need to re-initialize your icesat2data class object and log in to Earthdata
            and can then skip immediately to the download_granules method with restart=True.

        Notes
        -----
        This function is used by icesat2data.Icesat2Data.download_granules(), which automatically
        feeds in the required parameters.
        
        See Also
        --------
        icesat2data.Icesat2Data.download_granules
        """
        """
        extract : boolean, default False
            Unzip the downloaded granules.
        """

        #Note: need to test these checks still
        if session is None:
            raise ValueError("Don't forget to log in to Earthdata using is2_data.earthdata_login(uid, email)")
            #DevGoal: make this a more robust check for an active session

        #DevNote: this will replace any existing orderIDs with the saved list (could create confusion depending on whether download was interrupted or kernel restarted)
        order_fn  = '.order_restart'
        if os.path.exists( order_fn ):
            with open(order_fn,'r') as fid:
                order_dat = json.load(fid)
                self.orderIDs = order_dat['orderIDs']
        
        if not hasattr(self,'orderIDs') or len(self.orderIDs)==0:
            raise ValueError('Please confirm that you have submitted a valid order and it has successfully completed.')
            
        #DevNote: Temporary. Hard code the orderID info files here. order_fn should be consistent with place_order.         
        
        downid_fn = '.download_ID'
        
        i_order = 0
        
        if restart:       
            print('Restarting download ... ')
           
            # --- update the starting point of download list        
            if os.path.exists( downid_fn ):
                order_start = str(int( np.loadtxt(downid_fn) ) )
                i_order = self.orderIDs.index(order_start) + 1  
    
        for order in self.orderIDs[i_order:]:
            downloadURL = 'https://n5eil02u.ecs.nsidc.org/esir/' + order + '.zip'
            #DevGoal: get the download_url from the granules

 
            if verbose is True:
                print('Zip download URL: ', downloadURL)
            print('Beginning download of zipped output...')
            zip_response = session.get(downloadURL)
            # Raise bad request: Loop will stop for bad response code.
            zip_response.raise_for_status()
            print('Data request', order, 'of ', len(self.orderIDs[i_order:]), ' order(s) is downloaded.')

        #DevGoal: move this option back out to the is2class level and implement it in an alternate way?
        #         #Note: extract the dataset to save it locally
        # if extract is True:    
            with zipfile.ZipFile(io.BytesIO(zip_response.content)) as z:
                for zfile in z.filelist:
                    # Remove the subfolder name from the filepath
                    zfile.filename = os.path.basename(zfile.filename)
                    z.extract(member=zfile, path=path)
            
            # update the current finished order id and save to file
            with open(downid_fn,'w') as fid:
                fid.write( order )
        
        # remove orderID and download id files at the end 
        if os.path.exists( order_fn ): os.remove(order_fn)
        if os.path.exists( downid_fn ): os.remove(downid_fn)
        
        print('Download complete')
        