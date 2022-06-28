import datetime as dt
import os
import warnings
import numpy as np

import icepyx.core.APIformatting as apifmt


def prod_version(latest_vers, version):
    """
    Check if the submitted product version is valid, and warn the user if a newer version is available.
    """
    if version is None:
        vers = latest_vers
    else:
        if isinstance(version, str):
            assert int(version) > 0, "Version number must be positive"
            vers_length = 3
            vers = version.zfill(vers_length)
        else:
            raise TypeError("Please enter the version number as a string")

        if int(vers) < int(latest_vers):
            warnings.filterwarnings("always")
            warnings.warn("You are using an old version of this product")

    return vers


def cycles(cycle):
    """
    Check if the submitted cycle is valid, and warn the user if not available.
    """
    cycle_length = 2
    # number of GPS seconds between the GPS epoch and ATLAS SDP epoch
    atlas_sdp_gps_epoch = 1198800018.0
    # number of GPS seconds since the GPS epoch for first ATLAS data point
    atlas_gps_start_time = atlas_sdp_gps_epoch + 24710205.39202261
    epoch1 = dt.datetime(1980, 1, 6, 0, 0, 0)
    epoch2 = dt.datetime(1970, 1, 1, 0, 0, 0)
    # get the total number of seconds since the start of ATLAS and now
    delta_time_epochs = (epoch2 - epoch1).total_seconds()
    atlas_UNIX_start_time = atlas_gps_start_time - delta_time_epochs
    present_time = dt.datetime.now().timestamp()
    # divide total time by cycle length to get the maximum number of orbital cycles
    ncycles = np.ceil((present_time - atlas_UNIX_start_time) / (86400 * 91)).astype("i")
    all_cycles = [str(c + 1).zfill(cycle_length) for c in range(ncycles)]

    if cycle is None:
        return []
    else:
        if isinstance(cycle, str):
            assert int(cycle) > 0, "Cycle number must be positive"
            cycle_list = [cycle.zfill(cycle_length)]
        elif isinstance(cycle, int):
            assert cycle > 0, "Cycle number must be positive"
            cycle_list = [str(cycle).zfill(cycle_length)]
        elif isinstance(cycle, list):
            cycle_list = []
            for c in cycle:
                assert int(c) > 0, "Cycle number must be positive"
                cycle_list.append(str(c).zfill(cycle_length))
        else:
            raise TypeError("Please enter the cycle number as a list or string")

        # check if user-entered cycle is outside of currently available range
        if not set(all_cycles) & set(cycle_list):
            warnings.filterwarnings("always")
            warnings.warn("Listed cycle is not presently available")

        return cycle_list


def tracks(track):
    """
    Check if the submitted RGT is valid, and warn the user if not available.
    """
    track_length = 4
    # total number of ICESat-2 satellite RGTs is 1387
    all_tracks = [str(tr + 1).zfill(track_length) for tr in range(1387)]

    if track is None:
        return []
    else:
        if isinstance(track, str):
            assert int(track) > 0, "Reference Ground Track must be positive"
            track_list = [track.zfill(track_length)]
        elif isinstance(track, int):
            assert track > 0, "Reference Ground Track must be positive"
            track_list = [str(track).zfill(track_length)]
        elif isinstance(track, list):
            track_list = []
            for t in track:
                assert int(t) > 0, "Reference Ground Track must be positive"
                track_list.append(str(t).zfill(track_length))
        else:
            raise TypeError(
                "Please enter the Reference Ground Track as a list or string"
            )

        # check if user-entered RGT is outside of the valid range
        if not set(all_tracks) & set(track_list):
            warnings.filterwarnings("always")
            warnings.warn("Listed Reference Ground Track is not available")

        return track_list

