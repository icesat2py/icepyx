# NOTE: This is just a (quick and dirty) test for the data object
# and file functionality while they are not implemented.

# NOTE: Perhaps `Files` below should be the class `Data` itself, and the method
# `get_vars()` in both classes `Query` and `Data` should return another `Data` object.

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
        print("Input files:\n", self._files)
        print("Output dir:\n", self._outdir)
        print("Variables:\n", self._variables)
        # ...

    def _print_attrs(self, name, obj):
        print(name)
        for key, val in obj.attrs.items():
            print("    %s: %s" % (key, val))

    def print_vars(self):
        with h5py.File(self.files[0], "r") as f:
            f.visititems(self._print_attrs)


# --------------------------------------------------------------------------
# Functions


def get_file_list(path):
    """Return list with file names from `path'."""

    if path.is_dir():
        # Path to dir
        file_list = list(path.glob("*.h5"))
    elif path.is_file():
        # Path to single file
        file_list = [path]
    else:
        # Path with wildcard
        file_list = list(path.parent.glob(path.name))

    return file_list


def _get_var_paths(vardict):
    return list(vardict.keys()), list(vardict.values())


def _get_vars(ifile=None, variables=None, ofile=None):

    if isinstance(variables, dict):
        names, variables = _get_var_paths(variables)
    else:
        names = [v.split("/")[-1] for v in variables]

    dsets = read_h5(ifile, variables)  # list -> list

    vardict = {name: dset for name, dset in zip(names, dsets)}

    save_h5(ofile, vardict)


def get_vars(files=None, variables=None, outdir=None):

    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)

    ofiles = []

    for ifile in files:
        ifile = Path(ifile)
        ofile = outdir / (ifile.name + '_reduced')

        _get_vars(ifile, variables, ofile)

        ofiles.append(ofile)

    return ofiles


def read_h5(fname=None, variables=None):
    """Return variables ['v1', 'v2', ..] from HDF5."""
    with h5py.File(fname, "r") as f:
        return [f[v][()] for v in variables]


def save_h5(fname=None, vardict=None, mode="a"):
    """Save variables {'v1': v1, 'v2': v2, ..} to HDF5."""
    with h5py.File(fname, mode) as f:
        for k, v in vardict.items():
            if k in f:
                f[k][:] = np.squeeze(v)  # update
            else:
                f[k] = np.squeeze(v)  # create
