from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys

sys.setrecursionlimit(10000)


# returns item-id, only if the name is unique in the index
def getItemIndex(itemList,name):
  matched=False
  for item in itemList:
    if unicode(re.split('/',item['value'])[0]).strip() == unicode(name):
      if matched:
        return None
      matched=True
      id=item['id']
  if matched:
    return id
  return None

  
def parseSiehe(inItem, itemList):
  soup=BeautifulSoup()
  sieheNames=''
  possLast=''
  sieheNameKeys='[\w]{3,}(?: von [\w]{3,}| [\w][\w]\.)?'
  saarbrMatch = re.match('(?u)(.*?siehe (?:auch )?)(Saarbr.cken, [\w]+)(.*)', inItem)
  sieheMatch =  re.match('(?u)(.*?siehe (?:auch )?)((?:'+sieheNameKeys+')(?:, (?:'+sieheNameKeys+'))*)(.*)', inItem)
  if saarbrMatch:
    sieheNames=[sieheMatch.group(2)]
  if sieheMatch:
    if not sieheNames:
      sieheNames = re.split(',|/',sieheMatch.group(2))
    indexRefsTag=soup.new_tag('index-refs')
    first=True
    for sieheName in sieheNames:
      name=sieheName.strip()
      id=getItemIndex (itemList, name)
      if id:
        indexRefTag=soup.new_tag('index-ref')
        indexRefTag['itemid']=id
        indexRefTag.append(sieheName)
        indexRefsTag.append(possLast)
        possLast=''
        if not first:
          indexRefsTag.append(',')
        indexRefsTag.append(indexRefTag)
        print(name +": siehe ist aufgeloest")
        first=False
      else:
        print(name +": siehe konnte nicht aufgeloest werden")
        possLast=possLast+','+sieheName
    
    if not first:
      outItem=sieheMatch.group(1)
      outItem += unicode(indexRefsTag)
      if possLast:
       outItem+=possLast     
    else:
      outItem=sieheMatch.group(1)+sieheMatch.group(2)

    outItem += parseSiehe(sieheMatch.group(3), itemList)
    sieheNames=''
    return outItem
  else:
    return inItem


# postprocesses the xml (Aufloesung von 'siehe'-Referenzen innerhalb des Indexes)
def index_xml_postprocess():
  '''
  Postprocesses the parsed xml index (index.xml). Solves the regest-references in the item header.
  '''
  print('postprocessing ..')    
  with codecs.open ('index26.xml', 'r', 'utf-8') as inFile:
    with codecs.open ('index26_post.xml', 'w', 'utf-8') as outFile: # TODO 'a'
      inXml=inFile.read()
      inXmlSoup = BeautifulSoup(inXml)
      itemList=inXmlSoup.find_all('item')
      print(len(itemList))
      lines=inXml.split('\n')
      
      for line in lines:
        line=re.sub('&lt;', '<', line)  # necessary due to some encoding problems
        line=re.sub('&gt;','>', line)  # necessary due to some encoding problems
        if "index-refs" in line:
          headerMatch = re.match('(.*?)(<.*?-header.*?-header>)(.*)',line)
          header=headerMatch.group(2)
          header=re.sub('<.?index-refs>','', header)
          outItem=headerMatch.group(1)+parseSiehe(header, itemList)+headerMatch.group(3)
        else:
          outItem=line
        outFile.write(outItem)
        outFile.write("\n")
  print ('postprocessing done!')
  
if __name__=='main':
  index_xml_postprocess()