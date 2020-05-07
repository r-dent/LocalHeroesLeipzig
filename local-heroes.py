# MIT License

# Copyright (c) 2020 Roman Gille

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import urllib.request
import json
import time
import os
import sys
import math
import re
import webscraping
from difflib import SequenceMatcher

GMapsApiKey = ''
websiteUrl = 'http://local-heroes-leipzig.de/look-and-support/'
cacheFileName = 'data/local-heroes.json'
cityCenter = (51.3396955, 12.3730747)

def areSimilar(a, b):
    return SequenceMatcher(None, a, b).ratio() > 0.9

def findLocationGMaps(locationName):
    # geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + GMapsApiKey + '&address=' + urllib.parse.quote(locationName)
    geocodeUrl = 'https://maps.googleapis.com/maps/api/place/textsearch/json?key={key}&query={query}&location={lat},{lon}&radius={radius}'.format(
        key = GMapsApiKey,
        query = urllib.parse.quote(locationName),
        lat = cityCenter[0],
        lon = cityCenter[1],
        radius = 5000
    )

    print("Loading Location for %s." % locationName)

    with urllib.request.urlopen(geocodeUrl) as response:
        content = response.read()
        results = json.loads(content)['results']

        if len(results) > 0:
            firstResult = results[0]

            location = {
                'lat': firstResult['geometry']['location']['lat'], 
                'lon': firstResult['geometry']['location']['lng'],
                'address': firstResult['formatted_address'],
                'tags': firstResult['types']
            }

            print('Found %s.' % location)

        else:
            location = None
            print('NOT FOUND')

        return location

def findLocationOSM(locationName):
    geocodeUrl = "https://nominatim.openstreetmap.org/search?format=json&q="+ urllib.parse.quote(locationName)
    
    print("Loading Location for %s." % locationName)

    with urllib.request.urlopen(geocodeUrl) as response:
        content = response.read()
        results = json.loads(content)

        if len(results) > 0:
            firstResult = results[0]

            latitute = firstResult['lat']
            longitude = firstResult['lon']
            location = {'lat': latitute, 'lon': longitude}

            print('Found %s.' % location)

        else:
            location = None
            print('NOT FOUND')

        return location

def locationDistance(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

def addLocation(entries, updateAll = False, updateNoneEntries = False):
    for entry in entries:
        if updateAll or not('location' in entry) or (updateNoneEntries and entry['location'] == None):
            entry['location'] = findLocationGMaps(entry['title'].replace('/', ''))
            # time.sleep(1)
    return entries

def addOrUpdate(entries, updates):
    newEntries = []
    for update in updates:
        for entry in entries:
            if areSimilar(entry['title'], update['title']) and 'location' in entry:
                update['location'] = entry['location']
                break
        
        if 'location' in update and update['location'] != None:   
            dist = locationDistance(cityCenter, (update['location']['lat'], update['location']['lon']))
            if dist > 20000:
                continue

        newEntries.append(update)
    return newEntries

def showStats(entries):
    multiLocationRegEx = re.compile('[0-9]x', re.IGNORECASE)
    print(len(entries), 'Entries')
    print(sum('location' in e and e['location'] == None for e in entries), 'without location')
    print(sum(not('location' in e) for e in entries), 'with unchecked location')
    print(sum(bool(multiLocationRegEx.search(e['title'])) for e in entries), 'with multiple locations')

def loadEntriesFromFile(filePath):
    fileHandler = open(filePath, "r")
    return json.load(fileHandler)

def writeJson(data, filePath):
    fileHandler = open(filePath, "w")
    json.dump(data, fileHandler, indent=4, ensure_ascii=False)

def writeGeoJson(entries):
    geoEntries = []

    for entry in entries:
        if 'location' not in entry:
            continue

        location = entry['location']

        if location is None:
            continue
        
        coordinate = [location['lon'], location['lat']]
        tags = location.get('tags', [])
        uri = urllib.parse.urlparse(entry['link'])
        pathComponents = [comp for comp in uri.path.split('/') if comp != '']
        isLocality = False

        linkPath = ''
        if len(pathComponents) == 1 :
            linkPath = '/' + pathComponents[0]
        elif len(pathComponents) > 1:
            linkPath = uri.path[:20] + '...'

        for locationType in tags:
            if 'locality' in locationType:
                isLocality = True
                break

        if isLocality:
            continue

        geoEntry = {
            'type': 'Feature',
            'properties': {
                'name': entry['title'],
                'image': entry['image'],
                'description': entry['description'] + '<br>Link: <a href="' + entry['link'] + '" target="_blank">' + uri.netloc + linkPath + '</a>',
                'url': entry['link'],
                'address': location.get('address', ''),
                'category': entry['category'],
                'tags': tags
            },
            'geometry': {
                'type': 'Point',
                'coordinates': coordinate
            }
        }
        geoEntries.append(geoEntry)

    geoCollection = {
        'type': 'FeatureCollection',
        'features': geoEntries
    }

    writeJson(geoCollection, 'data/local-heroes-leipzig.geojson')


# --------
# Commands
# --------

entries = loadEntriesFromFile(cacheFileName)

if 'loadApi' in sys.argv:
    # Load api data to cache.
    newEntries = webscraping.loadLocalsFromWebsite(websiteUrl)
    entries = addOrUpdate(entries, newEntries)

if 'refreshAllLocations' in sys.argv:
    # Update all location data.
    entries = addLocation(entries, updateAll = True)

elif 'refreshNoneLocations' in sys.argv:
    # Update location data where its missing or was not found.
    entries = addLocation(entries, updateNoneEntries = True)

elif 'updateLocations' in sys.argv:
    # Update location data where its missing
    entries = addLocation(entries)

elif 'geocode' in sys.argv and len(sys.argv) == 3:
    findLocationGMaps(sys.argv[2])

if 'stats' in sys.argv:
    showStats(entries)

if 'debug' in sys.argv:
    print('No location founf for:')
    for e in entries:
        if 'location' not in e or e['location'] == None:
            print(e['title'], 'https://www.google.com/maps/search/' + e['title'].replace('/','').replace(' ','+'))

if 'writeGeoJson' in sys.argv:
    writeGeoJson(entries)

if 'writeCache' in sys.argv:
    writeJson(entries, cacheFileName)

if len(sys.argv) == 1:
    print('No parameter given.')
