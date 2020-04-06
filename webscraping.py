import urllib
import json
import html
from lxml import etree
from pyquery import PyQuery as pq # https://pypi.org/project/pyquery/

def loadLocalsFromWebsite(url):
    with urllib.request.urlopen(url) as response:
        content = response.read()
        d = pq(content)

        entries = []
        elements = d('.vc-parent-row.row-default .wpb_text_column.wpb_content_element.post-formatting .wpb_wrapper')
        currentCategory = None
        
        for element in elements:
            header = d('h2', element)
            if len(header) > 0:
                currentCategory = header.text()
            else:
                if currentCategory == None:
                    print('No category found. Stop parsing.')
                    break
                link = d('a:last', element)
                image = d('img', element)
                subCategory = html.unescape(image.attr('alt').split(' - ')[0].strip())

                if subCategory == '':
                    subCategory = 'Sonstiges'

                if subCategory == 'Pizza':
                    subCategory = 'Essen & Trinken'

                entry = {
                    'image': image.attr('src'),
                    'title': link.text(),
                    'link': link.attr('href'),
                    'sub-category': subCategory,
                    'category': currentCategory,
                    'cleanTitle': link.text().split('/ ')[0].strip(),
                    'description': html.unescape(d('p', element).text())
                }
                entries.append(entry)

        return entries

