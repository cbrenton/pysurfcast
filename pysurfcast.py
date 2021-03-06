#!/usr/bin/env python

import os.path
import sys
import getopt
import urllib.request
import time
from PIL import Image, ImageDraw
from datetime import date, timedelta, datetime
from xml.etree import ElementTree as ET

defaultSpot = 147
filepath = os.path.realpath(__file__)
homeprefix = filepath[:filepath.rfind('/')]
dataDir = homeprefix + '/data/'
imageDir = homeprefix + '/images/'

red = '\033[31m'
yellow = '\033[33m'
greenblink = '\033[5;32m'
endcolor = '\033[0m'

reds = [199, 160, 126, 69, 22]
blues = [237, 222, 206, 181, 147]
greens = [232, 214, 202, 196, 165]

prefs = {'verbose' : 0,
         'spotId' : defaultSpot}

"""
Parse the commandline options.
Store options in the global 'prefs' dict,
and return the remaining arguments.
"""
def getPrefs():
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hps:tv")
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == '-h':
            prefs['help'] = 1
        if o == '-p':
            prefs['printSpot'] = 1
        if o == '-s':
            prefs['spotId'] = a
        if o == '-t':
            prefs['text'] = 1
        elif o == '-v':
            prefs['verbose'] += 1
    return args

"""
Print the given message if and only if the verbose level is high enough.
"""
def log(msg, priority=1):
    if prefs['verbose'] >= priority:
        print >> sys.stderr, msg

"""
Print usage information.
"""
def usage():
    print("Usage:  %s [spotid] [options]" % os.path.basename(sys.argv[0]))

"""
Determine if the data file exists and is up to date.
"""
def hasCurrentData(dataFile):
    # Make the data directory if it doesn't exist.
    if not os.path.exists(dataDir):
        os.makedirs(dataDir)
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

"""
Takes a letter representing a shape (from 'p' for poor, to 'g' for good),
and returns a number representing the shape between 0 (poor) and 4 (good).
"""
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

"""
Colorizes the size data text to be output based on shape.
"""
def formatData(sizeText, shapeRank):
    if shapeRank == 1:
        return red + sizeText + endcolor
    elif shapeRank == 2:
        return sizeText
    elif shapeRank == 3:
        return yellow + sizeText + endcolor
    elif shapeRank == 4:
        return greenblink + sizeText + endcolor
    else:
        return ''

"""
Converts a string containing 12-hour time plus "AM" or "PM" to
24-hour time.
"""
def make24(hourtext):
    amPm = hourtext[-2:]
    hourNum = int(hourtext[:-2])
    hourNum %= 12
    if amPm == 'PM':
        hourNum += 12
    elif amPm == 'AM' and hourNum == 12:
        hourNum = 0
    return hourNum

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

"""
Find the size and number of circles to draw.
"""
def calculateCircles(element, printSpotName = False):
    spotName = element.getroot().find('NAME').text
    date = element.getroot().find('DATE').text
    #print('Forecast for %s on %s:' % (spotName, date))
    # Make list of all FORECAST elements in feed data.
    forecastList = element.getroot().findall('FORECAST')
    forecastDataList = []
    totalSize = 0
    currentShape = 0
    # TODO: Use a running average of the next few hours as wave size.
    currentSize = 0
    sizes = {}
    # FOR each forecast element
    for forecast in forecastList:
        # Find the relevant elements in the current forecast.
        size = forecast.find('SIZE').text
        hour = make24(forecast.find('HOUR').text)
        if hour == datetime.now().hour:
            shape = convertShape(forecast.find('SHAPE').text) + 1
            currentSize = int(size)
        totalSize += int(size)
        sizes[hour] = int(size)
    # Find the maximum wave size for the day to calculate border size.
    absMaxSize = max(sizes.values())
    generateCircles(spotName, int(shape), currentSize, absMaxSize)

"""
Draw the circles based on the already calculated data.
"""
def generateCircles(spotName, numCircles, circleSize, border = 1):
    # TODO: Add more buffer on the sides for large bordars.
    c = 50
    maxHeight = 8.0
    circleSize = int(min(circleSize, maxHeight) / maxHeight * c)
    #print('circle size: %d' % circleSize)
    gap = c / 2
    maxCircles = 5
    outfile = imageDir + spotName.lower().replace(" ", "") + ".png"
    imageWidth = int(c * maxCircles + gap * (maxCircles - 0.75))
    imageHeight = int(c + gap)
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
    # Make the images directory if it doesn't exist.
    if not os.path.exists(imageDir):
        os.makedirs(imageDir)
    im.save(outfile, "PNG")
    #print('written to %s' % outfile)

"""
Prints the forecast data as colored text.
"""
# TODO: Add a non-colored option.
def printTextForecast(element):
    spotName = element.getroot().find('NAME').text
    date = element.getroot().find('DATE').text
    # Make list of all FORECAST elements in feed data.
    forecastList = element.getroot().findall('FORECAST')
    forecastDataList = []
    maxSize = max([int(x.find('SIZE').text) for x in forecastList])
    minSize = min([int(x.find('SIZE').text) for x in forecastList])
    print('Forecast for %s on %s:' % (spotName, date))
    # FOR each forecast element
    for forecast in forecastList:
        # Find the relevant elements in the current forecast.
        size = forecast.find('SIZE').text
        shape = convertShape(forecast.find('SHAPE').text)
        hour = make24(forecast.find('HOUR').text)
        day = forecast.find('DAY').text
        curForecastData = {'size':size, 'shape':shape, 'hour':hour}
        forecastDataList.append(curForecastData)
        # If shape is less than "fair", do not print conditions.
        #if shape < 2:
            #continue
        timeStr = '%s\t:' % hour
        dataStr = ''
        for sizeNdx in range(int(size)):
            dataStr += '.'
        dataStr += '|'
        print('%s%s' % (timeStr, formatData(dataStr, shape)))
    for heightIndex in range(maxSize + 1):
        height = maxSize - heightIndex
        for forecastData in forecastDataList:
            #print '%d ?= %d ?= %d' % (minSize, height, maxSize)
            if minSize == height:
                sys.stdout.write('-')
            elif maxSize == height:
                sys.stdout.write('=')
            elif maxSize > height and minSize < height:
                sys.stdout.write('|')
            else:
                sys.stdout.write(' ')
        print('')

def main(argv=None):
    args = getPrefs()
    log('PREFS: %s' % prefs)
    if 'help' in prefs:
        usage()
        sys.exit(2)
    spotId = prefs['spotId']
    feedUrl = 'http://www.spitcast.com/api/spot/forecast/' + str(spotId) + '/?dcat=day&format=xml'
    feedPath = dataDir + 'data' + str(spotId) + '.xml'
    # IF forecast data is current.
    if hasCurrentData(feedPath):
        # Parse the forecast data from the file.
        element = ET.parse(feedPath)
    # IF forecast data is from a previous day.
    else:
        # Retrieve feed data.
        try:
            feed = urllib.request.urlopen(feedUrl)
        except:
            print('Could not retrieve forecast data from %s' % getFeedUrl())
            exit()
        # Parse the retrieved forecast data.
        element = ET.parse(feed)
        # Write the data to the data file.
        element.write(feedPath)
    if 'text' in prefs:
        printTextForecast(element)
    if 'printSpot' in prefs:
        spotName = element.getroot().find('NAME').text
        print(spotName)
    calculateCircles(element, True)

if __name__ == '__main__':
    main()
