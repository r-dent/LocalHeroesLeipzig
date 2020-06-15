import urllib
import json
import html
import ntpath
import os
from lxml import etree
from pyquery import PyQuery as pq # https://pypi.org/project/pyquery/

imagesFolder = 'data/imagecache/'

def loadLocalsFromWebsite(url):

    print('Loading', url, '...')

    with urllib.request.urlopen(url) as response:
        content = response.read()
        d = pq(content)

        entries = []
        categories = d("#content > div.grid-container")
        os.makedirs(imagesFolder, exist_ok=True)
        imagesCached = [f for f in os.listdir(imagesFolder) if os.path.isfile(os.path.join(imagesFolder, f))]

        print('Found', len(categories), 'categories.\nAlready fetched', len(imagesCached), 'images.')
        
        for category in categories:

            elements = d('.cat-items .post.item', category)
            categoryTitle = d('h2:first', category).text()

            print('Found', len(elements), 'elements in category', categoryTitle)

            for element in elements:

                image = d('img', element)
                imagePath = image.attr('src')
                imageFilename = ntpath.basename(imagePath)

                # Fix for multi-char umlaut.
                imageFilename = imageFilename.replace('ö', 'oe')

                if imageFilename not in imagesCached:
                    saveImage(imagePath, imageFilename)
                    imagesCached.append(imageFilename)

                link = d('a:last', element)
                subCategory = html.unescape(image.attr('alt').split(' - ')[0].strip())

                if subCategory == '':
                    subCategory = 'Sonstiges'

                if subCategory == 'Pizza':
                    subCategory = 'Essen & Trinken'

                entry = {
                    'image': imageFilename,
                    'title': link.text(),
                    'link': link.attr('href'),
                    'sub-category': subCategory,
                    'category': categoryTitle,
                    'cleanTitle': link.text().split('/ ')[0].strip(),
                    'description': html.unescape(d('p', element).text())
                }
                entries.append(entry)

        print('Parsed', len(entries), 'entries in', len(categories), "categories overall.")
        return entries

def saveImage(url, filename):
    filePath = imagesFolder + filename
    if os.path.exists(filePath):
        return

    print('Saving', url, 'to', filePath)
    url = urllib.request.quote(url, safe=':/')
    urllib.request.urlretrieve(url, filePath) 
