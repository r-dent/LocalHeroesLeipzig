import urllib.request
import json
import time
import os
import sys
import math
import html
from difflib import SequenceMatcher

GMapsApiKey = ''
wrapApiKey = ''
apiUrl = 'https://wrapapi.com/use/r-dent/side-projects/local-hero/latest?wrapAPIKey=' + wrapApiKey
cacheFileName = 'local-heroes.json'
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

def loadLocalsFromApi():
    with urllib.request.urlopen(apiUrl) as response:
        content = response.read()
        parsed_json = json.loads(content)
        entries = parsed_json['data']['output']
        titles = []
        localHeroes = []

        for entry in entries:
            title = entry['title'].split('/ ')[0].strip()

            if title not in titles:
                titles.append(title)
                entry['cleanTitle'] = title
                localHeroes.append(entry)

        return localHeroes

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

def addLocation(entries, updateAll = False):
    for entry in entries:
        if updateAll or not('location' in entry) or entry['location'] == None:
            entry['location'] = findLocationGMaps(entry['title'].replace('/', ''))
            # time.sleep(1)
    return entries

def addOrUpdate(entries, updates):
    newEntries = []
    for update in updates:
        for entry in entries:
            if areSimilar(entry['title'], update['title']) and 'location' in entry and entry['location'] != None:
                update['location'] = entry['location']
                break
        
        if 'location' in update and update['location'] != None:   
            dist = locationDistance(cityCenter, (update['location']['lat'], update['location']['lon']))
            if dist > 20000:
                continue

        newEntries.append(update)
    return newEntries

def showStats(entries):
    print(len(entries), 'Entries')
    print(sum(not('location' in e) or e['location'] == None for e in entries), 'without location')
    print(sum(e['category'] == '' for e in entries), 'without category')
    print(sum('>' in e['category'] for e in entries), 'with messy category')

def loadEntriesFromFile(filePath):
    fileHandler = open(filePath, "r")
    return json.load(fileHandler)

def writeJson(data, filePath):
    fileHandler = open(filePath, "w")
    json.dump(data, fileHandler, indent=4)

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
        isLocality = False

        for locationType in tags:
            if 'locality' in locationType:
                isLocality = True
                break

        if isLocality:
            continue

        category = html.unescape(entry['category'])
        if category == '':
            category = 'Sonstiges'

        geoEntry = {
            'type': 'Feature',
            'properties': {
                'name': entry['title'],
                'description': '<a href="' + entry['link'] + '">' + entry['link'] + '</a>',
                'url': entry['link'],
                'address': location.get('address', ''),
                'category': category,
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

    writeJson(geoCollection, 'local-heroes-leipzig.geojson')


# --------
# Commands
# --------

entries = loadEntriesFromFile(cacheFileName)

if 'refreshAllLocations' in sys.argv:
    # Update all location data.
    entries = addLocation(entries, updateAll = True)

elif 'updateLocations' in sys.argv:
    # Update location data where its missing
    entries = addLocation(entries)

elif 'loadApi' in sys.argv:
    # Load api data to cache.
    newEntries = loadLocalsFromApi()
    entries = addOrUpdate(entries, newEntries)

elif 'geocode' in sys.argv and len(sys.argv) == 3:
    findLocationGMaps(sys.argv[2])

if 'stats' in sys.argv:
    showStats(entries)

if 'debug' in sys.argv:
    for e in entries:
        if e['location'] != None:
            dist = locationDistance(cityCenter, (e['location']['lat'], e['location']['lon']))
            if dist > 20000:
                print('dist to', e['cleanTitle'], '-', dist)
                print('Address:', e['location']['address'])
                print('is HUUUUGE')

if 'writeGeoJson' in sys.argv:
    writeGeoJson(entries)

if 'writeCache' in sys.argv:
    writeJson(entries, cacheFileName)

if len(sys.argv) == 1:
    print('No parameter given.')
