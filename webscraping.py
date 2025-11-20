import urllib.request
import html
import os
from pyquery import PyQuery as pq # https://pypi.org/project/pyquery/

imagesFolder = 'data/imagecache/'

def loadLocalsFromWebsite(url):

    print('Loading', url, '...')

    with urllib.request.urlopen(url) as response:
        content = response.read()
        d = pq(content)

        entries = []
        categories = d('#content > div.grid-container')
        availableDistricts = {}
        os.makedirs(imagesFolder, exist_ok=True)
        imagesCached = [f for f in os.listdir(imagesFolder) if os.path.isfile(os.path.join(imagesFolder, f))]

        print('Found', len(categories), 'categories.\nAlready fetched', len(imagesCached), 'images.')
        
        for category in categories:

            elements = d('.cat-items .post.item', category)
            availableSubCategories = {}
            categoryTitle = d('h2:first', category).text()

            for subCategoryItem in d('.options a.option.category', category):
                subCategoryItem = d(subCategoryItem)
                availableSubCategories[subCategoryItem.attr('data-filter-value')] = subCategoryItem.text()

            for tagFilterItem in d('.options a.option.tag', category):
                tagFilterItem = d(tagFilterItem)
                availableDistricts[tagFilterItem.attr('data-filter-value')] = tagFilterItem.text()

            print('Found', len(elements), 'elements in category', categoryTitle, '\nSub.categories:\n -', '\n - '.join(availableSubCategories.values()), '\n')

            for element in elements:

                classes = set()
                for cssClass in d(element).attr('class').split(' '):
                    cssClass = cssClass.strip()
                    if cssClass != '':
                        classes.add(cssClass)

                image = d('img', element)
                imagePath = image.attr('src')
                imageFilename = os.path.basename(imagePath)

                # Fix for multi-char umlaut.
                imageFilename = imageFilename.replace('ö', 'oe')

                if imageFilename not in imagesCached:
                    saveImage(imagePath, imageFilename)
                    imagesCached.append(imageFilename)

                link = d('a:last', element)
                
                subCategories = []
                for subCategoryKey in classes & availableSubCategories.keys():
                    subCategories.append(availableSubCategories[subCategoryKey])
                
                districts = []
                for districtKey in classes & availableDistricts.keys():
                    districts.append(availableDistricts[districtKey])

                entry = {
                    'image': imageFilename,
                    'title': link.text(),
                    'link': link.attr('href'),
                    'sub-categories': sorted(subCategories),
                    'districts': sorted(districts),
                    'category': categoryTitle,
                    'cleanTitle': link.text().split('/ ')[0].strip(),
                    'description': html.unescape(d('p', element).text())
                }
                entries.append(entry)

        print('Parsed', len(entries), 'entries in', len(categories), 'categories\nDistricts:\n -', '\n - '.join(availableDistricts.values()))
        return entries

def saveImage(url, filename):
    filePath = imagesFolder + filename
    if os.path.exists(filePath):
        return

    print('Saving', url, 'to', filePath)
    url = urllib.request.quote(url, safe=':/')
    urllib.request.urlretrieve(url, filePath) 
