""" This module extracts the bibliography of the Sbr Regesten. """

import codecs, re
from bs4 import BeautifulSoup

#print('reached bibl file')

def indent_bibl():
  with codecs.open('bibl.xml', 'r', 'utf-8') as biblfile:
    with codecs.open('sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
      for line in biblfile:
        xmlfile.write('  '+line)


def extract_bibliography():
  print ('extracting bibliography..')
  #text = codecs.open('html/sbr-regesten.html', 'r', 'cp1252').read()
  text = codecs.open('html/sbr-regesten.html', 'r', 'cp1252').read()

  text=unicode(text)
  soup = BeautifulSoup(text)

  id=0
  #bibls=[]
  foundBibl = False
  #print ('extracting bibliography..')
  biblListTag=soup.new_tag('listBibl')
  biblInfoTag= soup.new_tag('listBibl-info')
  biblListTag.append(biblInfoTag)

  htmlItems=soup.findAll('p')
  foundBibl=False
  nextBiblInfo=False
  for htmlItem in htmlItems:
    if htmlItem.get_text().strip()!='' and htmlItem.get_text()!='\n' and htmlItem.get_text()!= "\r":
      if htmlItem.get_text().startswith('Abk'):
        break
      
      if htmlItem.get_text().startswith('Literaturverzeichnis'):
        biblListTag.append(htmlItem.get_text())
        foundBibl=True
        nextBiblInfo=True
        print('Bibl gefunden')
        continue
       
      elif nextBiblInfo:
        print('found bibl-info')
        biblInfoTag.append(htmlItem.get_text())
        biblListTag.append(biblInfoTag)
        #biblInfoTag.append('\n')
        nextBiblInfo=False
        continue

      if foundBibl:
        item=htmlItem.get_text()
        biblTag=soup.new_tag('bibl')
        biblTag['id']='bibl_'+str(id)
        id+=1
        biblTag.append(item)
        biblListTag.append(biblTag)

  with codecs.open('bibl.xml', 'w', 'utf-8') as biblfile:
    biblfile.write('\n'+unicode(biblListTag.prettify())+'\n')
  
  indent_bibl()


if __name__=='main':
  extract_bibliography()