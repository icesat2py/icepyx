import os
import re
import h5py
import zarr
import itertools
import numpy as np

# PURPOSE: Wrapper function for converting HDF5 files to different formats
def file_converter(hdf5_file, path, reformat):
    """
    Wrapper function for converting HDF5 files to different formats
    """
    if (reformat == 'zarr'):
        # output zarr file
        HDF5_to_zarr(hdf5_file, path)
    # elif (reformat == 'JPL'):
    #     # output JPL captoolkit formatted HDF5 files
    #     HDF5_to_JPL_HDF5(hdf5_file, path)
    elif reformat in ('csv','txt'):
        # output reduced files to ascii formats
        HDF5_to_ascii(hdf5_file, path, reformat)

# PURPOSE: convert the HDF5 file to zarr copying all file data
def HDF5_to_zarr(hdf5_file, path):
    """
    convert the HDF5 file to zarr copying all file data
    """
    # split extension from HDF5 file
    fileBasename,fileExtension = os.path.splitext(hdf5_file.filename)
    zarr_file = os.path.join(path,'{0}.zarr'.format(fileBasename))
    # copy everything from the HDF5 file to the zarr file
    with h5py.File(hdf5_file,mode='r') as source:
        dest = zarr.open_group(zarr_file,mode='w')
        # value checks on output zarr
        if not hasattr(dest, 'create_dataset'):
            raise ValueError('dest must be a group, got {!r}'.format(dest))
        # for each key in the root of the hdf5 file structure
        for k in source.keys():
            copy_from_HDF5(source[k], dest, name=k)

# PURPOSE: Copy a named variable from the HDF5 file to the zarr file
def copy_from_HDF5(source, dest, name, **create_kws):
    """Copy a named variable from the `source` HDF5 into the `dest` zarr"""
    if hasattr(source, 'shape'):
        # copy a dataset/array
        if dest is not None and name in dest:
            raise CopyError('an object {!r} already exists in destination '
                '{!r}'.format(name, dest.name))
        # setup creation keyword arguments
        kws = create_kws.copy()
        # setup chunks option, preserve by default
        kws.setdefault('chunks', source.chunks)
        # setup compression options
        # from h5py to zarr: use zarr default compression options
        kws.setdefault('fill_value', source.fillvalue)
        # create new dataset in destination
        ds=dest.create_dataset(name,shape=source.shape,dtype=source.dtype,**kws)
        # copy data going chunk by chunk to avoid loading in entirety
        shape = ds.shape
        chunks = ds.chunks
        chunk_offsets = [range(0, s, c) for s, c in zip(shape, chunks)]
        for offset in itertools.product(*chunk_offsets):
            sel = tuple(slice(o, min(s, o + c)) for o, s, c in
                zip(offset, shape, chunks))
            ds[sel] = source[sel]
        # copy attributes
        attrs = {key:attributes_encoder(source.attrs[key]) for key in
            source.attrs.keys() if attributes_encoder(source.attrs[key])}
        ds.attrs.update(attrs)
    else:
        # copy a group
        if (dest is not None and name in dest and hasattr(dest[name], 'shape')):
            raise CopyError('an array {!r} already exists in destination '
                '{!r}'.format(name, dest.name))
        # require group in destination
        grp = dest.require_group(name)
        # copy attributes
        attrs = {key:attributes_encoder(source.attrs[key]) for key in
            source.attrs.keys() if attributes_encoder(source.attrs[key])}
        grp.attrs.update(attrs)
        # recursively copy from source
        for k in source.keys():
            copy_from_HDF5(source[k], grp, name=k)

# PURPOSE: reduce HDF5 files to beam groups and output to ascii
def HDF5_to_ascii(hdf5_file, path, reformat):
    """
    convert the HDF5 file to beam-level ascii files copying reduced sets of data
    """
    # split extension from HDF5 file
    fileBasename,fileExtension = os.path.splitext(hdf5_file.filename)
    delimiter = ',' if reformat == 'csv' else '\t'
    # copy bare minimum variables from the HDF5 file to the zarr file
    source = h5py.File(hdf5_file,mode='r')
    # compile regular expression operator for extracting info from ICESat2 files
    rx = re.compile(r'(processed)?(ATL\d+)(-\d{{2}})?_(\d{4})(\d{2})(\d{2})'
        r'(\d{2})(\d{2})(\d{2})_(\d{4})(\d{2})(\d{2})_(\d{3})_(\d{2})(.*?).h5$')
    # extract parameters from ICESat2 HDF5 file
    SUB,PRD,HEM,YY,MM,DD,HH,MN,SS,TRK,CYCL,GRAN,RL,VERS,AUX = \
        rx.findall(os.path.basename(hdf5_file.filename)).pop()
    # find valid beam groups by testing for particular variables
    if (PRD == 'ATL06'):
        VARIABLE_PATH = ['land_ice_segments','segment_id']
    elif (PRD == 'ATL07'):
        VARIABLE_PATH = ['sea_ice_segments','height_segment_id']
    elif (PRD == 'ATL08'):
        VARIABLE_PATH = ['land_segments','segment_id_beg']
    elif (PRD == 'ATL10'):
        VARIABLE_PATH = ['freeboard_beam_segments','delta_time']
    elif (PRD == 'ATL12'):
        VARIABLE_PATH = ['ssh_segments']['delta_time']
    # create list of valid beams within the HDF5 file
    beams = []
    for gtx in [k for k in source.keys() if bool(re.match(r'gt\d[lr]',k))]:
        # check if subsetted beam contains data
        try:
            source['/'.join([gtx,*VARIABLE_PATH])]
        except KeyError:
            pass
        else:
            beams.append(gtx)

    # for each valid beam within the HDF5 file
    for gtx in sorted(beams):
        # create a column stack of valid output segment values
        if (PRD == 'ATL06'):
            var = source[gtx]['land_ice_segments']
            valid, = np.nonzero(var['atl06_quality_summary'][:] == 0)
            # variables for the output ascii file
            vnames = ['segment_id','delta_time','latitude','longitude','h_li']
            vformat = '{1:0.0f}{0}{2:0.9f}{0}{3:0.9f}{0}{4:0.9f}{0}{5:0.9f}'
            # extract attributes for each variable
            vattrs = {}
            for i,v in enumerate(vnames):
                vattrs[v] = {atn:atv for atn,atv in var[v].attrs.items()}
                if (v == 'segment_id'):
                    vattrs[v]['precision'] = 'integer'
                    vattrs[v]['units'] = 'count'
                else:
                    vattrs[v]['precision'] = 'double_precision'
                vattrs[v]['comments'] = 'column {0:d}'.format(i+1)
            # column stack of valid output segment values
            output = np.column_stack([var[v][valid] for v in vnames])

        # output ascii file
        ascii_file = '{0}_{1}.{2}'.format(fileBasename,gtx,reformat)
        fid = open(os.path.join(path,ascii_file),'w')
        # print YAML header to top of file
        fid.write('{0}:\n'.format('header'))
        # global attributes for file
        fid.write('  {0}:\n'.format('global_attributes'))
        for atn,atv in source.attrs.items():
            if atn not in ('Conventions','Processing Parameters','hdfversion',
                'history','identifier_file_uuid'):
                fid.write('    {0:22}: {1}\n'.format(atn,attributes_encoder(atv)))
        # beam attributes
        fid.write('\n  {0}:\n'.format('beam_attributes'))
        for atn,atv in source[gtx].attrs.items():
            if atn not in ('Description',):
                fid.write('    {0:22}: {1}\n'.format(atn,attributes_encoder(atv)))
        # data dimensions
        fid.write('\n  {0}:\n'.format('dimensions'))
        nrow,ncol = np.shape(output)
        fid.write('    {0:22}: {1:d}\n'.format('segments',nrow))
        # non-standard attributes
        fid.write('\n  {0}:\n'.format('non-standard_attributes'))
        # value to convert to GPS seconds (seconds since 1980-01-06T00:00:00)
        fid.write('    {0:22}:\n'.format('atlas_sdp_gps_epoch'))
        atlas_sdp_gps_epoch = source['ancillary_data']['atlas_sdp_gps_epoch']
        for atn in ['units','long_name']:
            atv = attributes_encoder(atlas_sdp_gps_epoch.attrs[atn])
            fid.write('      {0:20}: {1}\n'.format(atn,atv))
        fid.write('      {0:20}: {1:0.0f}\n'.format('value',atlas_sdp_gps_epoch[0]))
        # print variable descriptions to YAML header
        fid.write('\n  {0}:\n'.format('variables'))
        for v in vnames:
            fid.write('    {0:22}:\n'.format(v))
            for atn in ['precision','units','long_name','comments']:
                atv = attributes_encoder(vattrs[v][atn])
                fid.write('      {0:20}: {1}\n'.format(atn,atv))
        # end of header
        fid.write('\n\n# End of YAML header\n')
        # print data to file
        for row in output:
            print(vformat.format(delimiter,*row),file=fid)
        # close the file
        fid.close()
    # close the source HDF5 file
    source.close()

# PURPOSE: encoder for copying the file attributes
def attributes_encoder(attr):
    """Custom encoder for copying file attributes in Python 3"""
    if isinstance(attr, (bytes, bytearray)):
        return attr.decode('utf-8')
    if isinstance(attr, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32,
        np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(attr)
    elif isinstance(attr, (np.float_, np.float16, np.float32, np.float64)):
        return float(attr)
    elif isinstance(attr, (np.ndarray)):
        if not isinstance(attr[0], (object)):
            return attr.tolist()
    elif isinstance(attr, (np.bool_)):
        return bool(attr)
    elif isinstance(attr, (np.void)):
        return None
    else:
        return attr
