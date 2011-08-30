#!/usr/bin/env/python

import os.path
import sys
import time
from datetime import date
import urllib
from xml.etree import ElementTree as ET

feedUrl = "http://www.spitcast.com/api/spot/forecast/147/?dcat=week&format=xml"
feedPath = "data.xml"

# Determine if the data file exists and is up to date.
def hasCurrentData():
    # IF file exists
    if os.path.isfile(feedPath):
        # Get modified date of file.
        modDate = date.fromtimestamp(os.path.getmtime(feedPath))
        # Get today's date.
        today = date.today();
        # IF the modified date is before today's date
        if today > modDate:
            return False
        else:
            return True

def main():
    # IF forecast data is current.
    if hasCurrentData():
        print "forecast file exists and is up to date"
        # Parse the forecast data from the file.
        element = ET.parse(feedPath)
    # IF forecast data is from a previous day.
    else:
        print "retrieving forecast data from url"
        # Retrieve feed data.
        feed = urllib.urlopen(feedUrl)
        # Parse the retrieved forecast data.
        element = ET.parse(feed)
        # Write the data to the data file.
        element.write(feedPath)
    # Make list of all FORECAST elements in feed data.
    forecastList = element.getroot().findall("FORECAST")
    # FOR each forecast element
    for forecast in forecastList:
        # Find the relevant elements in the current forecast.
        size = forecast.find("SIZE").text
        maxSize = int(forecast.find("SIZE_MAXIMUM").text)
        minSize = int(forecast.find("SIZE_MINIMUM").text)
        shape = forecast.find("SHAPE").text
        hour = forecast.find("HOUR").text
        day = forecast.find("DAY").text
        #print "Hour: %s on %s\nSize: %s (%s - %s)\nShape: %s\n" % \
                #(hour, day, size, minSize, maxSize, shape)
        sys.stdout.write("%s\t:" % (hour))
        for sizeNdx in range(int(maxSize) + 1):
            if sizeNdx < minSize:
                sys.stdout.write(".")
            elif sizeNdx == minSize or sizeNdx == maxSize:
                sys.stdout.write("|")
            else:
                sys.stdout.write("-")
        print ""

if __name__ == "__main__":
    main()
