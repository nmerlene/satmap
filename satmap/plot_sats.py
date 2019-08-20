#!/usr/bin/env python
"""
Plot GNSS satellite positions
"""

from __future__ import print_function, division, absolute_import

import datetime as dt
from argparse import ArgumentParser

import matplotlib.pyplot as plt

import satmap
from satmap import utils


def parse_args():
    """
    Extract inputs from command line

    Returns:
        args (argparse.NameSpace): Argparse namespace object
    """
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=satmap.ArgumentFormatter,
        parents=[satmap.get_parent_argparse()],
    )
    parser.add_argument(
        "-t",
        "--plot-type",
        help="Plot type",
        choices=("polar_azel", "ground_track"),
        default="polar_azel",
    )
    parser.add_argument("-f", "--figure", help="File name to save figure to")
    return parser.parse_args()


def main():
    """
    Main entry point for script.

    Returns:
        0 = successful, 1 = unsuccessful
    """
    args = parse_args()
    start_time = satmap.script_setup(args.verbose, args.quiet)
    data = utils.get_location_data()
    lat, lon = utils.get_current_latlon(data)
    observer = utils.get_observer(lat, lon)
    sat_groups = utils.read_tle_files()
    sat_groups = utils.compute_sat_positions(sat_groups, observer)
    if args.plot_type.lower() == "ground_track":
        fig = utils.plot_ground_tracks(sat_groups)
    else:
        fig = utils.plot_polar_azel(sat_groups)
        loc = "{}, {}".format(data["city"], data["region"])
        fig.suptitle(
            "Visible Satellites above {} at {} (UTC)".format(
                loc, dt.datetime.now().strftime("%d %b %Y %H:%M:%S")
            )
        )
    if args.figure:
        fig.savefig(args.figure, dpi=150)
    else:
        plt.show()
    satmap.script_teardown(start_time)

    return 0


if __name__ == "__main__":
    main()
