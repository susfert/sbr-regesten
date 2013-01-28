""" This module extracts the bibliography of the Sbr Regesten. """

import codecs
import re
import glob
import os
from bs4 import BeautifulSoup

def indent_bibl():
    '''Indents the bibliography before writing it into sbr-regesten.xml'''
    with codecs.open('bibl_tmp.xml', 'r', 'utf-8') as biblfile:
        with codecs.open('sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
            for line in biblfile:
                xmlfile.write('  ' + line)


def extract_bibliography():
    '''Extracts the bibliography part of the sbr-regensten from sbr-regesten.html.'''
    print ('extracting bibliography..')
    text = codecs.open('html/sbr-regesten.html', 'r', 'cp1252').read()

    text = unicode(text)
    soup = BeautifulSoup(text)

    id = 0
    foundBibl = False
    biblListTag = soup.new_tag('listBibl')
    biblInfoTag = soup.new_tag('listBibl-info')
    biblListTag.append(biblInfoTag)

    htmlItems = soup.findAll('p')
    foundBibl = False
    nextBiblInfo = False
    for htmlItem in htmlItems:
        item_text = htmlItem.get_text()
        if htmlItem.get_text().strip() != '' and item_text != '\n' and item_text != '\r':
            if item_text.startswith('Abk'):
                break
            
            if item_text.startswith('Literaturverzeichnis'):
                biblListTag.append(item_text)
                foundBibl = True
                nextBiblInfo = True
                continue
             
            elif nextBiblInfo:
                biblInfoTag.append(item_text)
                biblListTag.append(biblInfoTag)
                nextBiblInfo = False
                continue

            if foundBibl:
                item = htmlItem.get_text()
                biblTag=soup.new_tag('bibl')
                biblTag['id'] = 'bibl_' + str(id)
                id += 1
                biblTag.append(item)
                biblListTag.append(biblTag)

    with codecs.open('bibl_tmp.xml', 'w', 'utf-8') as biblfile:
        biblfile.write('\n' + unicode(biblListTag.prettify()) + '\n')
    
    indent_bibl()
    os.remove('bibl_tmp.xml')


if __name__ == 'main':
    extract_bibliography()
