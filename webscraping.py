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
        elements = d('.vc-parent-row.row-default .wpb_text_column.wpb_content_element.post-formatting .wpb_wrapper')
        currentCategory = None
        os.makedirs(imagesFolder, exist_ok=True)
        imagesCached = [f for f in os.listdir(imagesFolder) if os.path.isfile(os.path.join(imagesFolder, f))]

        print('Found', len(elements), 'businesses. Already fetched', len(imagesCached), 'images.')
        
        for element in elements:
            header = d('h2', element)
            if len(header) > 0:
                currentCategory = header.text()
            else:
                if currentCategory == None:
                    print('No category found. Stop parsing.')
                    break

                image = d('img', element)
                imagePath = image.attr('src')
                imageFilename = ntpath.basename(imagePath)
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
                    'category': currentCategory,
                    'cleanTitle': link.text().split('/ ')[0].strip(),
                    'description': html.unescape(d('p', element).text())
                }
                entries.append(entry)

        return entries

def saveImage(url, filename):
    filePath = imagesFolder + filename
    if os.path.exists(filePath):
        return

    print('Saving', url, 'to', filePath)
    url = urllib.request.quote(url, safe=':/')
    urllib.request.urlretrieve(url, filePath) 
