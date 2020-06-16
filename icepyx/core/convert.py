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
    # split extension from zfile
    fileBasename,fileExtension = os.path.splitext(hdf5_file.filename)
    if (reformat == 'zarr'):
        # output zarr file
        zarr_file = os.path.join(path,'{0}.zarr'.format(fileBasename))
        HDF5_to_zarr(hdf5_file, zarr_file)
    # elif (reformat == 'JPL'):
    #     # output JPL captoolkit formatted HDF5 files
    #     HDF5_to_JPL_HDF5(hdf5_file)
    # elif reformat in ('csv','txt'):
    #     # output reduced files to ascii formats
    #     delimiter = ',' if reformat == 'csv' else '\t'
    #     HDF5_to_ascii(hdf5_file, delimiter)

# PURPOSE: convert the HDF5 file to zarr copying all file data
def HDF5_to_zarr(hdf5_file, zarr_file):
    """
    convert the HDF5 file to zarr copying all file data
    """
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
