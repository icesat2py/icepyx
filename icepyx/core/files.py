# NOTE: This is just a (quick and dirty) test for the data object
# and file functionality while they are not implemented.

# XXX: Perhaps `Files` below should be the class `Data`, and the method `get_vars()`
# in both classes `Query` and `Data` should return another `Data` object.

import h5py
import numpy as np
from pathlib import Path


class Files():
    """Interact with ICESat-2 data files locally."""

    def __init__(self, files=None, variables=None, outdir=None):

        # TODO: Properly validate all inputs.

        self._files = files
        self._variables = variables
        self._outdir = Path(outdir).resolve()

    @property
    def files(self):
        return self._files

    @property
    def variables(self):
        return self._variables

    @property
    def outdir(self):
        return self._outdir

    # ----------------------------------------------------------------------
    # Methods

    def info(self):
        print("Input files:", self._files)
        print("Output dir:", self._outdir)
        print("Variables:", self._variables)
        # ...


def get_file_list(path):
    """Return list with file names from `path'."""

    if path.is_dir():
        file_list = list(path.glob("*"))
    elif path.is_file():
        file_list = [path]
    else:
        file_list = list(path.parent.glob(path.name))

    return file_list


def get_vars(*args):
    pass


def _get_vars(fname=None, variables=None, outdir=None):
    # Here variables is a list with full paths
    dsets = read_h5(fname, variables)  # -> list
    ddsets = {v.split("/")[-1]: v for v in dsets}  # -> dict
    self.save_h5(fname + "_reduced", ddsets)


def get_vars():
    pass


def _print_attrs(self, name, obj):
    print(name)
    for key, val in obj.attrs.items():
        print("    %s: %s" % (key, val))


def print_vars(self, fname=None):
    with h5py.File(fname, "r") as f:
        f.visititems(self._print_attrs)


def read_h5(self, fname=None, variables=None):
    """Return variables ['v1', 'v2', ..] from HDF5."""
    with h5py.File(fname, "r") as f:
        return [f[v][()] for v in variables]


def save_h5(self, fname=None, vardict=None, mode="a"):
    """Save variables {'v1': v1, 'v2': v2, ..} to HDF5."""
    with h5py.File(fname, mode) as f:
        for k, v in vardict.items():
            if k in f:
                f[k][:] = np.squeeze(v)  # update
            else:
                f[k] = np.squeeze(v)  # create
'''
