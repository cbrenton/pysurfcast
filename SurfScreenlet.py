#!/usr/bin/env python

import os.path
import sys
import Image, ImageDraw
import time
from datetime import date, timedelta, datetime
import urllib
from xml.etree import ElementTree as ET

defaultSpot = '147'

red = '\033[31m'
yellow = '\033[33m'
greenblink = '\033[5;32m'
endcolor = '\033[0m'

reds = [199, 160, 126, 69, 22]
blues = [237, 222, 206, 181, 147]
greens = [232, 214, 202, 196, 165]

# Print usage information.
def usage():
    print("Usage:  %s" % os.path.basename(sys.argv[0]))

# Determine if the data file exists and is up to date.
def hasCurrentData(dataFile):
    # IF file exists
    if os.path.isfile(dataFile):
        # Get modified date of file.
        modDate = date.fromtimestamp(os.path.getmtime(dataFile))
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
    if shapeLetter == 'p':
        return 0
    elif shapeLetter == 'pf':
        return 1
    elif shapeLetter == 'f':
        return 2
    elif shapeLetter == 'fg':
        return 3
    elif shapeLetter == 'g':
        return 4

def formatData(sizeText, shapeRank):
    if shapeRank == 2:
        return red + sizeText + endcolor
    elif shapeRank == 3:
        return yellow + sizeText + endcolor
    elif shapeRank == 4:
        return greenblink + sizeText + endcolor
    else:
        return ''

# Converts a string containing 12-hour time plus "AM" or "PM" to
# 24-hour rime.
def make24(hourtext):
    amPm = hourtext[-2:]
    hourNum = int(hourtext[:-2])
    hourNum %= 12
    if amPm == 'PM':
        hourNum += 12
    elif amPm == 'AM' and hourNum == 12:
        hourNum = 0
    return hourNum

def calculateCircles(element):
    spotName = element.getroot().find('NAME').text
    date = element.getroot().find('DATE').text
    absMaxSize = int(element.getroot().find('SIZE_MAX').text)
    absMinSize = int(element.getroot().find('SIZE_MIN').text)
    #print('Forecast for %s on %s:' % (spotName, date))
    # Make list of all FORECAST elements in feed data.
    forecastList = element.getroot().findall('FORECAST')
    forecastDataList = []
    #totalShape = 0
    totalSize = 0
    currentShape = 0
    # FOR each forecast element
    for forecast in forecastList:
        # Find the relevant elements in the current forecast.
        size = forecast.find('SIZE').text
        hour = make24(forecast.find('HOUR').text)
        if hour == datetime.now().hour:
            shape = convertShape(forecast.find('SHAPE').text)
        totalSize += int(size)
    avgSize = totalSize / len(forecastList)
    #print('height: %d - %d, %d' % (absMinSize, absMaxSize, avgSize))
    generateCircles(spotName, int(shape), avgSize, absMaxSize - absMinSize)

def generateCircles(spotName, numCircles, circleSize, border = 1):
    c = 50
    maxHeight = 8.0
    circleSize = int(min(circleSize, maxHeight) / maxHeight * c)
    #print('circle size: %d' % circleSize)
    gap = c / 2
    maxCircles = 5
    outfile = spotName.lower().replace(" ", "") + ".png"
    imageWidth = int(c * maxCircles + gap * (maxCircles - 0.75))
    imageHeight = c + gap
    im = Image.new("RGBA", (imageWidth, imageHeight), (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    startX = gap / 8 + c / 2
    startY = gap / 2 + c / 2
    rad1 = circleSize / 2 + border
    rad2 = circleSize / 2
    for i in range(maxCircles - numCircles, maxCircles):
        curX = startX + (c + gap) * i
        colorNdx = min(i - (maxCircles - numCircles), len(reds))
        r = reds[colorNdx]
        g = greens[colorNdx]
        b = blues[colorNdx]
        dr.ellipse((curX - rad1, startY - rad1, curX + rad1, startY + rad1), fill=(55, 55, 55))
        dr.ellipse((curX - rad2, startY - rad2, curX + rad2, startY + rad2), fill=(r, g, b))
    im.save(outfile, "PNG")
    #print('written to %s' % outfile)

def printTextForecast(element):
    spotName = element.getroot().find('NAME').text
    date = element.getroot().find('DATE').text
    absMaxSize = int(element.getroot().find('SIZE_MAX').text)
    print('Forecast for %s on %s:' % (spotName, date))
    # Make list of all FORECAST elements in feed data.
    forecastList = element.getroot().findall('FORECAST')
    forecastDataList = []
    # FOR each forecast element
    for forecast in forecastList:
        # Find the relevant elements in the current forecast.
        size = forecast.find('SIZE').text
        maxSize = int(forecast.find('SIZE_MAXIMUM').text)
        minSize = int(forecast.find('SIZE_MINIMUM').text)
        shape = convertShape(forecast.find('SHAPE').text)
        hour = make24(forecast.find('HOUR').text)
        day = forecast.find('DAY').text
        curForecastData = {'size':size, 'minSize':minSize, 'maxSize':maxSize, \
                'shape':shape, 'hour':hour}
        forecastDataList.append(curForecastData)
        # If shape is less than "fair", do not print conditions.
        if shape < 2:
            continue
        timeStr = '%s\t:' % hour
        # Get today's date.
        #today = date.today();
        # Calculate tomorrow's date.
        #tomorrow = today + timedelta(1)
        dataStr = ''
        for sizeNdx in range(int(maxSize) + 1):
            if sizeNdx < minSize:
                dataStr += '.'
            elif sizeNdx == minSize or sizeNdx == maxSize:
                dataStr += '|'
            else:
                dataStr += '='
        print('%s%s' % (timeStr, formatData(dataStr, shape)))
    for heightIndex in range(absMaxSize + 1):
        height = absMaxSize - heightIndex
        for forecastData in forecastDataList:
            if forecastData['minSize'] == height:
                sys.stdout.write('-')
            elif forecastData['maxSize'] == height:
                sys.stdout.write('=')
            elif forecastData['maxSize'] > height and \
                    forecastData['minSize'] < height:
                        sys.stdout.write('|')
            else:
                sys.stdout.write(' ')
            #sys.stdout.write("%s" % forecastData['minSize']),
        print('')

def main(argv=None):
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        usage()
        sys.exit(2)
    if len(sys.argv) > 1:
        spotId = sys.argv[1]
    else:
        spotId = defaultSpot
    #if "-b" in args or "--best" in args:
        #spotId = ;
    feedUrl = 'http://www.spitcast.com/api/spot/forecast/' + spotId + '/?dcat=day&format=xml'
    feedPath = 'data' + spotId + '.xml'
    # IF forecast data is current.
    if hasCurrentData(feedPath):
        # Parse the forecast data from the file.
        element = ET.parse(feedPath)
    # IF forecast data is from a previous day.
    else:
        # Retrieve feed data.
        try:
            feed = urllib.urlopen(feedUrl)
        except:
            print('Could not retrieve forecast data from %s' % getFeedUrl())
            exit()
        # Parse the retrieved forecast data.
        element = ET.parse(feed)
        # Write the data to the data file.
        element.write(feedPath)
    if "-t" in args or "--text" in args:
        printTextForecast(element)
    else:
        calculateCircles(element)

if __name__ == "__main__":
    main()
