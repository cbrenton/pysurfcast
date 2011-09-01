#!/usr/bin/env/python

import os.path
import sys
import time
from termcolor import colored
from datetime import date, timedelta
import urllib
from xml.etree import ElementTree as ET

spotId = "147"
feedUrl = "http://www.spitcast.com/api/spot/forecast/" + spotId + "/?dcat=day&format=xml"
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

# Takes a letter representing a shape (from 'p' for poor, to 'g' for good),
# and returns a number representing the shape between 0 (poor) and 4 (good).
def convertShape(shapeLetter):
    if shapeLetter == "p":
        return 0
    elif shapeLetter == "pf":
        return 1
    elif shapeLetter == "f":
        return 2
    elif shapeLetter == "fg":
        return 3
    elif shapeLetter == "g":
        return 4

def formatData(sizeText, shapeRank):
    if shapeRank == 2:
        return colored(sizeText, 'yellow')
    elif shapeRank == 3:
        return colored(sizeText, 'green')
    elif shapeRank == 4:
        return colored(sizeText, 'green', attrs=['blink'])
    else:
        return ""

# Converts a string containing 12-hour time plus "AM" or "PM" to
# 24-hour rime.
def make24(hourtext):
    amPm = hourtext[-2:]
    hourNum = int(hourtext[:-2])
    hourNum %= 12
    if amPm == "PM":
        hourNum += 12
    elif amPm == "AM" and hourNum == 12:
        hourNum = 0
    return hourNum

def main():
    # IF forecast data is current.
    if hasCurrentData():
        # Parse the forecast data from the file.
        element = ET.parse(feedPath)
    # IF forecast data is from a previous day.
    else:
        # Retrieve feed data.
        try:
            feed = urllib.urlopen(feedUrl)
        except:
            print "Could not retrieve forecast data."
            exit()
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
        shape = convertShape(forecast.find("SHAPE").text)
        hour = make24(forecast.find("HOUR").text)
        day = forecast.find("DAY").text
        # If shape is less than "fair", do not print conditions.
        if shape < 2:
            continue
        #sys.stdout.write("%s\t:" % (hour))
        dataStr = ("%s\t:" % hour)
        # Get today's date.
        #today = date.today();
        # Calculate tomorrow's date.
        #tomorrow = today + timedelta(1)
        for sizeNdx in range(int(maxSize) + 1):
            if sizeNdx < minSize:
                dataStr += '.'
                #sys.stdout.write(".")
            elif sizeNdx == minSize or sizeNdx == maxSize:
                #sys.stdout.write("|")
                dataStr += '|'
            else:
                #sys.stdout.write("=")
                dataStr += '='
        #print ""
        print formatData(dataStr, shape)


if __name__ == "__main__":
    main()
