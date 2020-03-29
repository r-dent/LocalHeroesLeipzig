import urllib.request
import json
import time
import os

GMapsApiKey = ''
wrapApiKey = ''
apiUrl = 'https://wrapapi.com/use/r-dent/side-projects/local-hero/latest?wrapAPIKey=' + wrapApiKey
cacheFileName = 'local-heroes.json'

def findLocationGMaps(locationName):
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + GMapsApiKey + '&address=' + urllib.parse.quote(locationName)
    
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
                entry['location'] = findLocationGMaps(title + ' Leipzig')
                localHeroes.append(entry)
                # time.sleep(1)

        return localHeroes

def loadEntriesFromFile(filePath):
    fileHandler = open(filePath, "r")
    return json.load(fileHandler)

def writeJson(data, filePath):
    fileHandler = open(filePath, "w")
    json.dump(data, fileHandler, indent=4)

def writeGeoJson(entries):
    geoEntries = []

    for entry in entries:
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

        geoEntry = {
            'type': 'Feature',
            'properties': {
                'name': entry['title'],
                'description': '<a href="' + entry['link'] + '">' + entry['link'] + '</a>',
                'url': entry['link'],
                'address': location.get('address', ''),
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

# Load api date to cache.
# writeJson(loadLocalsFromApi(), cacheFileName)

# Generate geojson from cache.
writeGeoJson(loadEntriesFromFile(cacheFileName))
