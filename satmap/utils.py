#!/usr/bin/env python
"""
General utilities to support extracting GNSS satellite positions
"""

from __future__ import print_function, division, absolute_import

import os
import logging
import datetime as dt
from urllib.request import urlopen
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.basemap import Basemap

import ephem

LOGGER = logging.getLogger()

# TLE file list
TLE_FILES = (
    "https://www.celestrak.com/NORAD/elements/gps-ops.txt",
    "https://www.celestrak.com/NORAD/elements/glo-ops.txt",
    "https://www.celestrak.com/NORAD/elements/galileo.txt",
    "https://www.celestrak.com/NORAD/elements/beidou.txt",
    "https://www.celestrak.com/NORAD/elements/sbas.txt",
)


def get_location_data():
    """
    Extract location data based off IP address

    Returns:
        dict: Dictionary containing location data
    """
    LOGGER.info("Extracting location data based on IP address...")
    url = "http://ipinfo.io/json"
    response = urlopen(url)
    data = json.load(response)
    loc = "{}, {}".format(data["city"], data["region"])
    LOGGER.info("Location determined to be: %s", loc)
    return data


def get_current_latlon(data):
    """
    Extract current latitude and longitude (in degrees) based off of IP address

    Args:
        data (dict): Dictionary containing location data

    Returns:
        tuple(float, float): Two-element tuple containing latitude and longitude
    """
    lat, lon = data["loc"].split(",")
    return lat, lon


def get_observer(lat, lon, obs_time=dt.datetime.utcnow()):
    """
    Return a PyEphem observer object based off of the input latitude, longitude, and time

    Args:
        lat (float):            Latitude (degrees)
        lon (float):            Longitude (degrees)
        obs_time (dt.datetime): Observer time (in UTC)

    Returns:
        ephem.Observer: PyEphem observer
    """
    observer = ephem.Observer()
    observer.lon = lon
    observer.lat = lat
    observer.date = obs_time
    return observer


def read_tle_files(tle_files=TLE_FILES):
    """
    Read TLE files

    Args:
        tle_files (iter(str)): Iterable of URLs to TLE file(s)

    Returns:
        dict: Dictionary containing keys for each satellite group
    """
    sat_groups = dict()  # Initialize satellite group dictionary
    # Loop through each TLE file
    for tle_file in tle_files:
        # Satellite group name (parse from link name)
        sat_group = os.path.splitext(os.path.basename(tle_file))[0].upper()
        # Read TLEs from file
        LOGGER.info("Reading TLE file %s for satellite group %s", tle_file, sat_group)
        lines = urlopen(tle_file).read().decode("utf-8").splitlines()
        sats = []
        for ind_line, line in enumerate(lines):
            if ind_line % 3 == 2:
                sat = ephem.readtle(lines[ind_line - 2], lines[ind_line - 1], line)
                sats.append(sat)
        sat_groups[sat_group] = sats
    return sat_groups


def compute_sat_positions(sat_groups, observer):
    """
    Compute absolute and relative satellite positions using the observer object and TLE files

    Args:
        sat_groups (dict):         Dictionary containing keys for each satellite group
        observer (ephem.Observer): PyEphem observer

    Returns:
        dict: Dictionary containing keys for each satellite group
    """
    for sat_group in sat_groups.values():
        for sat in sat_group:
            sat.compute(observer)
    return sat_groups


def plot_polar_azel(sat_groups):
    """
    Generate a polar (azimuth/elevation) plot showing satellite positions relative to current
      location

    Args:
        sat_groups (dict): Dictionary containing keys for each satellite group

    Returns:
        fig: matplotlib.figure.Figure: Figure handle
    """
    # Initialize figure
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    # Create colormap based off of number of satellite groups
    colors = cm.nipy_spectral(np.linspace(0, 1, len(sat_groups)))
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    for ind_group, sat_group in enumerate(sat_groups.values()):
        # Exclude any satellites that are not in view (< 0 deg elevation angle)
        visible_sats = []
        for sat in sat_group:
            if sat.alt > 0:
                visible_sats.append(sat)
        # Plot satellites
        ax.scatter(
            [sat.az for sat in visible_sats],
            [90 - np.rad2deg(sat.alt) for sat in visible_sats],
            marker="+",
            color=colors[ind_group]
        )
        # Annotate with satellite name
        for visible_sat in visible_sats:
            ax.annotate(
                visible_sat.name,
                xy=(visible_sat.az, 90 - np.rad2deg(visible_sat.alt)),
                color=colors[ind_group],
                horizontalalignment='left',
                verticalalignment='bottom'
            )
    ax.set_yticks(range(0, 90 + 10, 10))
    ax.set_yticklabels(['90', '', '', '60', '', '', '30', '', '', ''])
    ax.grid(True)
    return fig


def plot_ground_tracks(sat_groups, obs_time=dt.datetime.utcnow()):
    """
    Generate plot of ground tracks

    Args:
        sat_groups (dict):      Dictionary containing keys for each satellite group
        obs_time (dt.datetime): Observer time (in UTC)

    Returns:
        fig: matplotlib.figure.Figure: Figure handle
    """
    # Initialize figure and map
    fig = plt.figure(figsize=(12, 10))
    # Create colormap based off of number of satellite groups
    colors = cm.nipy_spectral(np.linspace(0, 1, len(sat_groups)))
    m = Basemap(projection='mill')  # Use Miller project
    # Plot coastlines, draw label meridians and parallels.
    m.drawcoastlines()
    m.bluemarble(scale=0.2, alpha=0.95, zorder=-1)
    m.nightshade(obs_time, alpha=0.5, zorder=0)  # Add nightshade
    # Plot satellites by group
    for ind_group, (sat_group_key, sat_group) in enumerate(sat_groups.items()):
        lats = [np.rad2deg(sat.sublat) for sat in sat_group]
        lons = [np.rad2deg(sat.sublong) for sat in sat_group]
        x, y = m(lons, lats)  # transform coordinates
        m.scatter(x, y, s=40, marker='+', color=colors[ind_group],
                  label=sat_group_key)
    fig.suptitle('Visible Satellites at {} (UTC)'.format(obs_time.strftime("%d %b %Y %H:%M:%S")))
    fig.legend()
    return fig
