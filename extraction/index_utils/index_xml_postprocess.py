"""
This module postprocesses the index xml.

Author: Susanne Fertmann <s9sufert@stud.uni-saarland.de>
"""


import codecs
import string
import re
import sys
from bs4 import BeautifulSoup, Tag, NavigableString



def getItemIndex(itemList, name):
    ''' Find index item with a certain name (string). Return its id.'''
    matched = False
    for item in itemList:
        if unicode(re.split('/',item['value'])[0]).strip() == unicode(name):
            if matched:
                return None
            matched = True
            id = item['id']
    if matched:
            return id
    return None

    
def parseSiehe(inItem, itemList):
    '''
    Parse references to other index entries (index-refs). Find the
    single references in the index-refs tag, solve and tag them.
    '''
    soup=BeautifulSoup()
    sieheNames = ''
    possLast = ''
    sieheNameKeys = '[\w]{3,}(?: von [\w]{3,}| [\w][\w]\.)?'
    saarbrMatch = re.match('(?u)(.*?siehe (?:auch )?)(Saarbr.cken, [\w]+)'\
                           '(.*)', inItem)
    sieheMatch = re.match('(?u)(.*?siehe (?:auch )?)((?:'+sieheNameKeys+')'\
                          '(?:, (?:'+sieheNameKeys+'))*)(.*)', inItem)
    if saarbrMatch:
        sieheNames = [sieheMatch.group(2)]
    if sieheMatch:
        if not sieheNames:
            sieheNames = re.split(',|/',sieheMatch.group(2))
        indexRefsTag = soup.new_tag('index-refs')
        first = True
        for sieheName in sieheNames:
            name = sieheName.strip()
            id = getItemIndex (itemList, name)
            if id:
                indexRefTag = soup.new_tag('index-ref')
                indexRefTag['itemid'] = id
                indexRefTag.append(sieheName)
                indexRefsTag.append(possLast)
                possLast = ''
                if not first:
                    indexRefsTag.append(',')
                indexRefsTag.append(indexRefTag)
                #print(name + ": index-ref is solved")
                first = False
            else:
                print(name + ": index-ref could not be solved")
                possLast = possLast + ',' + sieheName
        
        if not first:
            outItem = sieheMatch.group(1)
            outItem += unicode(indexRefsTag)
            if possLast:
             outItem += possLast         
        else:
            outItem = sieheMatch.group(1) + sieheMatch.group(2)

        outItem += parseSiehe(sieheMatch.group(3), itemList)
        sieheNames = ''
        return outItem
    else:
        return inItem


def index_xml_postprocess():
    '''
    Postprocess the XML index. Solve references to other index entries
    in the item headers.
    '''
    print('Postprocessing index xml.')        
    with codecs.open ('index.xml', 'r', 'utf-8') as inFile:
        with codecs.open ('sbr-regesten.xml', 'a', 'utf-8') as outFile:
            outFile.write('\n')
            inXml = inFile.read()
            inXmlSoup = BeautifulSoup(inXml)
            itemList = inXmlSoup.find_all('item')
            lines = inXml.split('\n')
            
            for line in lines:
                line = re.sub('&lt;', '<', line)    # necessary due to some encoding problems
                line = re.sub('&gt;','>', line)     # necessary due to some encoding problems
                if "index-refs" in line:
                    headerMatch = re.match('(.*?)(<.*?-header.*?-header>)'\
                                           '(.*)', line)
                    header = headerMatch.group(2)
                    header = re.sub('<.?index-refs>','', header)
                    outItem = headerMatch.group(1) + parseSiehe(header, \
                              itemList) + headerMatch.group(3)
                else:
                    outItem = line
                outFile.write(outItem)
                outFile.write("\n")
                
            outFile.write('\n </sbr-regesten>')
    
    print ('postprocessing done!')
    
if __name__=='main':
    index_xml_postprocess()