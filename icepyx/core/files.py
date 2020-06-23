# NOTE: This is just a (quick and dirty) test for the data object
# and file functionality while they are not implemented.

# NOTE: Perhaps `Files` below should be the class `Data` itself, and the method
# `get_vars()` in both classes `Query` and `Data` should return another `Data` object.

from pathlib import Path

import h5py
import numpy as np


class Files(object):
    """Interact with ICESat-2 data files locally."""

    def __init__(self, files=None, variables=None, outdir=None, orig_files=None):

        # TODO: Properly validate all inputs.

        self._files = files
        self._variables = variables
        self._outdir = Path(outdir).resolve()
        self._orig_files = orig_files

    @property
    def files(self):
        return self._files

    @property
    def variables(self):
        return self._variables

    @property
    def outdir(self):
        return self._outdir

    @property
    def orig_files(self):
        return self._orig_files

    # ----------------------------------------------------------------------
    # Methods

    def info(self):
        print("\nInput files:\n", [f.name for f in self._orig_files])
        print("\nOutput files:\n", [f.name for f in self._files])
        print("\nData folder:\n", self._outdir)
        print("\nVariables:\n", self._variables)
        # ...

    def _print_attrs(self, name, obj):
        print(name)

        for key, val in obj.attrs.items():
            print("    %s: %s" % (key, val))

    def print_vars(self, fname=None):
        """Print attrs and variables of given file or first found."""

        if fname is None:
            fname = self.files[0]

        print("\nFile variables:")

        with h5py.File(fname, "r") as f:
            f.visititems(self._print_attrs)


# --------------------------------------------------------------------------
# Functions (these may/should be wrapped as class methods)

# Here we define easy mappings to variables in IS2 files.
_var_mapping = {
    "lon": "/gt1l/land_ice_segments/longitude",
    "lat": "/gt1l/land_ice_segments/latitude",
    "height": "/gt1l/land_ice_segments/h_li",
    # ...
}


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


def _get_key_value(vardict):
    """Return two lists with keys and values, respectively."""

    return list(vardict.keys()), list(vardict.values())


def _construct_var_name(varlist):
    """Return var name from /path/to/var as `var_path`."""

    return [(v.split("/")[-1] + "_" + v.split("/")[1]) for v in varlist]


def _get_name_path(variables, var_mapping):

    if isinstance(variables, dict):
        # User-defined names and paths
        names, variables = _get_key_value(variables)

    elif isinstance(variables, list) and all(
        v in _var_mapping.keys() for v in variables
    ):
        # User-provided var keys (to be mapped)
        subset = {k: v for k, v in var_mapping.items() if k in variables}
        names, variables = _get_key_value(subset)

    elif isinstance(variables, list):
        # User-provided paths only
        names = _construct_var_name(variables)

    else:
        names, variables = [], []

    return names, variables


def _get_vars(ifile=None, variables=None, ofile=None, var_mapping=_var_mapping):

    names, variables = _get_name_path(variables, var_mapping)

    dsets = read_h5(ifile, variables)  # list -> list

    vardict = {name: dset for name, dset in zip(names, dsets)}

    save_h5(ofile, vardict)


# TODO: Maybe this should be a method of `Files` that return a `Files` obj (self)?
def get_vars(files=None, variables=None, outdir=None):

    outdir = Path(outdir)
    outdir.mkdir(exist_ok=True)

    ofiles = []

    for ifile in files:
        ifile = Path(ifile)
        ofile = outdir / (ifile.name + "_reduced")

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
