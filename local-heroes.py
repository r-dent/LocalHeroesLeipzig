import urllib.request
import json
import time
import os

GMapsApiKey = ''
wrapApiKey = ''
apiUrl = 'https://wrapapi.com/use/r-dent/side-projects/local-hero/latest?wrapAPIKey=' + wrapApiKey

def findLocationGMaps(locationName):
    geocodeUrl = 'https://maps.googleapis.com/maps/api/geocode/json?key=' + GMapsApiKey + '&address=' + urllib.parse.quote(locationName)
    
    print("Loading Location for %s." % locationName)

    with urllib.request.urlopen(geocodeUrl) as response:
        content = response.read()
        results = json.loads(content)['results']

        if len(results) > 0:
            firstResult = results[0]

            latitute = firstResult['geometry']['location']['lat']
            longitude = firstResult['geometry']['location']['lng']
            location = {'lat': latitute, 'lon': longitude}

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

def startFile(filePath, binary=False):
    fileHandler = open(filePath, "wb" if (binary) else "w")
    return fileHandler

def writeGeoJson(entries):
    geoEntries = []
    for entry in entries:
        location = [entry['location']['lon'], entry['location']['lat']]
        geoEntry = {
            'type': 'Feature',
            'properties': {
                'name': entry['title'],
                'url': entry['link']
            },
            'geometry': {
                'type': 'Point',
                'coordinates': location
            }
        }
        geoEntries.append(geoEntry)

    outputFile = startFile('local-heroes-leipzig.geojson')
    json.dump(geoEntries, outputFile)

localHeroes = loadEntriesFromFile('local-heroes.json')
# localHeroes = loadLocalsFromApi()
writeGeoJson(localHeroes)

# print(findLocationGMaps('Kleine Leckerei Leipzig'))
# print(findLocationOSM('Kleine Leckerei Leipzig'))
