# 15-12-2012 Susanne Fertmann


from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys

from regesten_webapp import models
from regesten_webapp.models import Location, Family, Person, Region, PersonGroup, Landmark, Concept, IndexEntry, Regest, RegestDate

sys.setrecursionlimit(10000)


soup = BeautifulSoup()
forenames = []
persons = []
persongroups = []
locations = []
landmarks = []
unclassified = []
families = []
siehe = [] # to collect items that will be classified later through their reference with "siehe"

person_id = 0

########################## 1. Preprocessing ########################

# deletes all span-tags
def delSpan(s):
  s = re.sub('\</?span.*?\>','',s)
  return s


def joinb (s):
  ''' Joins b-tags in a string if there is nothing in between or only a comma. '''
  s = re.sub('(?u)(\</b\>)([(:?\<.*?\>), ]*)(\<b\>)','\g<2>', s)
  return s


  
def joini (s):
  ''' Joins i-tags in a string if there is nothing in between or only a comma. '''
  s = re.sub('(?u)(\</i\>)([(:?\<.*?\>), ]*)(\<i\>)','\g<2>', s)
  return s


  
def preprocess(soup):
  ''' Preprocesses the soup. '''
  print("Preprocessor is working..")
  s = unicode(soup)
  s = delSpan(s)
  s = joinb(s)
  s = joini(s)
  soup = BeautifulSoup(s)
  return soup


########################## 2. ItemExtractor ########################

class ExtractorException(Exception):
  def __init__(self, text):
    self.text = text
    
  def __str__(self):
    return self.text

class IndexItem:
  def __init__(self, header, body):
    self.header = header
    self.body = body
  def __repr__(self):
    return (str(self.header)+"\n"+str(self.body))+"\n"+"\n"



#########################################################################################################################
###############################################   3. ITEMPARSER   #######################################################
#########################################################################################################################

with codecs.open("sbr-regesten.xml", "r", "utf-8") as f:
  s = BeautifulSoup(f)
  regSoup = s.regesten
  regList = regSoup.findAll('regest')


def getRegID(reg_ref):
  ''' Seaches the restesten part of the xml to match a given reg-ref to its corresponding regest, returning its id.
      As the regesten part of the xml was not available during development, it's probably not fully working (not tested).
      If no regest is found, the default value of regest_0 (the first regest) will be returned.'''
  
  defaultID = "regest_0" #99999
  idList = []
  count = False
  countR = 0
  
  for reg in regList:
    if countR>10:
      break
    if count:
      countR += 1
    
    if reg.date.get_text().startswith(reg_ref):
      idList.append(reg['id'])
      count = True
      
  if len(idList) == 1:
    print('regest gefunden!!!!!')
    return idList[0]
  else:
    #print('keine eindeutige regestzuweisung moeglich:' + str(idList))
    return defaultID 
  
def findSiehe(text):
  indexRefsTag = None

  sieheMatch = re.match('(.*?)(m?i?t? [Ss]iehe[^0-9\)\(]*$)', text)
  if sieheMatch:
    text = sieheMatch.group(1)
    siehe = sieheMatch.group(2)
    print('siehe: '+ siehe)
    indexRefsTag = soup.new_tag('index-refs')
    indexRefsTag.append(siehe)
    
  return text, indexRefsTag


def parseMentionings(soup, t):
  '''
  Finds and tags mentionings in a given soup.
  '''
  mentioningsTag = None
  text = t
  mentionings = []
  ment = '((?:\[?\+\]? )?[01][0-9][0-9][0-9]\-?\/?[01]?[0-9]?\-?[0-3]?[0-9]? ?\([a-f]?k?u?r?z? ??n?a?c?h?v?o?r?n?t?e?u?m?p?o?s?t?a?n?t?e?\??\.?\) ?)( Anm\.)?|((?:\[?\+\]? )?[01][0-9][0-9][0-9]\-?[01]?[0-9]?\-?[0-3]?[0-9]? ?\(?z?w?i?s?c?h?e?n?\)?)'
  #1306-03-24 (?), 1504/1505 (a) Anm., 1431-1459 (zwischen)
  # TODO 1482-07-16 (nach) - 1499-01-08 (vor)
  
  mentMatch = re.match('(.*?)('+ment+',? ?)$', text)
  while mentMatch:
    text = mentMatch.group(1)
    menti = mentMatch.group(2)
    mentionings.insert(0, menti)
    mentMatch = re.match('(.*?)('+ment+'),\.? $', text)
  
  if mentionings:
    mentioningsTag = soup.new_tag("mentioned-in")
    notFirstEl = False
    for reg_ref in mentionings:
      if notFirstEl:
        mentioningsTag.append(', ')
      else:
        notFirstEl = True
      reg_refTag = soup.new_tag("reg-ref")
      reg_refTag.append(reg_ref)
      id = getRegID(reg_ref)
      reg_refTag['regest'] = id
      
      mentioningsTag.append(reg_refTag)
  return (text, mentioningsTag)

# parses additional names (which appear between parenthesis and are written in italics.)
def addNamesToXML(parentTag, text):
  altNMatch = re.match("(?u)(.*?\(\<i.*?\>)(.*?)\)(.*, .*)", text)
  r = None
  if altNMatch:
    altNames = BeautifulSoup(altNMatch.group(2)).get_text().strip().split(',') #TODO
    addNamesTag = soup.new_tag("addNames")
    addNamesTag.append(BeautifulSoup(altNMatch.group(1)).get_text())

    parentTag.append(addNamesTag)
    notFirstEl = False
    for altName in altNames:
      if notFirstEl:
         addNamesTag.append(',')
      else:
        notFirstEl = True
      addNameTag = soup.new_tag("addName")
      addNameTag.append(altName)
      addNamesTag.append(addNameTag)
    addNamesTag.append('')
    addNamesTag.append(')')
    r = altNMatch.group(3)
  return (parentTag, r)

# parses a person name
def parsePersName (nameTag, personName):
  foreTag = soup.new_tag("forename")
  
  genNameKeys = "der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\.|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|Junior|Jr|Senior|Sr|der Junge|der Alte"
  genNameMatch = re.search("(.*?)(\[?"+genNameKeys+"\]?)(.*)",personName)
  
  addNameMatch = re.search("(.*?)"+"(gen\.|den man nennet|dem man sprichet)"+"(.+)",personName)
  
  if genNameMatch:
    foreName = genNameMatch.group(1)
    if foreName.strip() != "":
      nameTag.append(foreTag)   
      foreTag.append(foreName) 
    genName = genNameMatch.group(2)
    restName = genNameMatch.group(3)
    genNameTag = soup.new_tag("genName")
    nameTag.append(genNameTag)
    genNameTag.append(genName)   
    nameTag.append(restName)
    
  elif addNameMatch:
    foreName = addNameMatch.group(1)
    gen = addNameMatch.group(2)
    addName = addNameMatch.group(3)
    if foreName.strip() != "":
      nameTag.append(foreTag)   
      foreTag.append(foreName) 
    addNamesTag = soup.new_tag("addNames")
    addNameTag = soup.new_tag("addName")
    nameTag.append(gen)
    nameTag.append(addNamesTag)
    addNamesTag.append(addNameTag)
    addNameTag.append(addName)
    
  else:
    nameTag.append(foreTag)   
    foreTag.append(personName)
    # nur ersten string als Vornamen??


def equalMatchGroup(match,i,label):
  try:
    return match.group(label) == match.group(i)
  except IndexError:
    return False
  
def getMatchLabel(match,i):
    matchDict = match.groupdict()
    for groupName in matchDict.keys():
      if equalMatchGroup(match,i,groupName):
        return groupName
    return None
    
def annotateGrNames(m, nameTag):
  for i in range(1,len(m.groups())+1):
    label = getMatchLabel(m,i)
    if label:
      label = label.replace('_','-')
    if label and m.group(i):
      labelTag = soup.new_tag(label)
      nameTag.append(labelTag)
      labelTag.append(m.group(i))
    else:
      nameTag.append(m.group(i))
  return nameTag, m.end(m.lastindex)


####################### 3.1. Header Parser ####################################

####################### 3.1.1 LocationHeader ####################################

def parsePlaceName (header, placeNameTag):

  # Wuestungen
  settleTag = soup.new_tag("settlement")
  placeNameTag.append(settleTag)
 
  wuestMatch = re.search('(Staerk, W.stungen Nr. [0-9][0-9]?)', header.get_text())
  w = False
  if wuestMatch:
    w = True      
    w_ref = wuestMatch.group(0)
    settleTag["w-ref"] = w_ref
  settleTag["w"] = str(w).lower()
 
  # Settlement name 
  name = ''
  rest = ''
  if header.b:                # for location-headers
    name = header.b.get_text()
    ohneB = BeautifulSoup(str(header))
    ohneB.b.decompose()
    rest = unicode(ohneB)
  
  else:                       # for locations in family headers
    liste = header.get_text().split(',', 1)
    name = liste[0]
    if len(liste) > 1:
      rest = liste[1]
    else:
      rest= ''
  
  
 
  settleTag.append(name)
  
  # SettlementType, RefPoint, District, Region, Country
  settlement = "Dorf|Stadt|Stadtteil|Burgsiedlung|Burg|ehem. Burg|Hofgut|Hof|Ort|.rtlichkeit|Gemeinde|Kloster|Abtei|Schloss|Herrschaft|Gft\.|Kgr\.|Land|Kgr\.|Herzogtum|Hzgt\.|Grafschaft|F.rstentum|Deutschordenskommende|Bistum|Vogtei|Regierungssitz|Hochstift|Pfarrei|Erzstift|Erzbistum|Dekanat|Domstift|Reichsland|Deutschordensballei|\w*abtei|Wasserburg|M.hle|Zisterzienserabtei|Region"
  districtKeys = "Gem|Stadtverband [^;,]+|Gde\. [^,;]+|[\w-]+-Kreis|Kr\. [^,;]+|[-\w]+kreis|Stadt [\w][\w]\.|Stadt [\w-]+|Kreis [^;,]+"
  district = "(?:"+districtKeys + ")(?:, (?:" + districtKeys + "))?"
  regionKeys = "Dep\.,? [A-Za-z-]+|SL|NRW|By|RLP|BW|Prov\..+|Hessen"
  country = "B|F|NL|CH|Lux|It|L|Spanien|T.rkei"
  settlementKeys = "(?:"+settlement+")(?![\w])"
  countryKeys = "(?:"+country+")(?![\w])"
  

  placeNameTag, ohneAddN = addNamesToXML(placeNameTag, rest)
  if ohneAddN:
    text = BeautifulSoup(ohneAddN).get_text()
  else:
    text = BeautifulSoup(rest).get_text()

  text, indexRefsTag = findSiehe(text)
  text, ment = parseMentionings(soup, text)
  
  settleMatch = re.match('(?u)(.*?)('+ settlementKeys +')(.*?)', text)
  
  if settleMatch:
    placeNameTag, index = annotateGrNames(settleMatch, placeNameTag)
    text = text[index:]
    settleTag["type"] = settleMatch.group(2)
  else:
    settleTag["type"] = 'unknown'
  
  
  distRegMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district + ')(.*)(?P<region>'+ regionKeys + ')(.*)', text)
  distRegCountMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district +')(.*)(?P<region>'+ regionKeys + ')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  distCountMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district +')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  regCountMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<region>'+ regionKeys + ')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  countMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<country>'+ countryKeys + ')(.*)', text)
  regMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<region>'+ regionKeys + ')(.*)', text)
  distMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district + ')(.*)', text)
  settleMatch = re.match('(?u)([^\w]?(?:siehe [\w/-]+)?)(?P<reference_point>[\w\.\/ -]*?)(.*)', text)
  
  possibleMatches = [distRegCountMatch, distRegMatch, distCountMatch,  regCountMatch, regMatch, distMatch, countMatch, settleMatch]
  for m in possibleMatches:
    if m:
      placeNameTag, index = annotateGrNames(m, placeNameTag)
      
      if "region" in m.groupdict():   
        region = m.group("region")
        if "Prov" in region:
          placeNameTag.find("region")['type'] = 'Provinz'
        elif "Dep" in region:
          placeNameTag.find("region")['type'] = 'Departement'
        elif "NRW" or "SL" or "RLP" or "By" or "BW" or "Hessen" in region:
          placeNameTag.find("region")['type'] = 'Bundesland'
          
      break

  return (placeNameTag, ment, name, indexRefsTag)


def locHeaderToXML(header):
  headerTag = soup.new_tag("location-header")
  placeNameTag = soup.new_tag('placeName')
  placeNameTag, ment, name, indexRefsTag = parsePlaceName(header, placeNameTag)
  
  headerTag.append(placeNameTag)
  
  if ment:
    headerTag.append(ment)
  if indexRefsTag:
    headerTag.append(indexRefsTag)
  
  if header.get_text().strip() != headerTag.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    print('\n')

  return name.rstrip(', '), headerTag


####################### 3.1.2 Family Header ####################################

def famHeaderToXML(header):
  ''' Converts the html of an item header into a xml header of the type family-header.'''
  headerTag = soup.new_tag("family-header")

  # Name
  name = header.b.get_text()
  famNameTag = soup.new_tag('family-name')
  nameTag = soup.new_tag('name')
  famNameTag.append(nameTag)
  nameTag.append(name)
  
  ohneB = BeautifulSoup(str(header))
  ohneB.b.decompose()
  

  # Alternative names & locations (both are in parentesis right after the name, alternative names are in italics, locations not)
  famNameTag, ohneAddN = addNamesToXML(famNameTag, unicode(ohneB))
  headerTag.append(famNameTag)
  
  if ohneAddN:
    rest = BeautifulSoup(ohneAddN).get_text()
  else:
    rest = ohneB.get_text()

  parMatch = re.match(r"([^\w]*?)\((.*[A-Za-z][a-z]{1,3}.*)(\), .*)", rest)
  if parMatch:
    headerTag.append(BeautifulSoup(parMatch.group(1)).get_text())
    loc = BeautifulSoup(parMatch.group(2))
    placeNameTag = soup.new_tag('location')
    placeNameTag, m, n, s = parsePlaceName(loc, placeNameTag)
    headerTag.append('(')
    headerTag.append(placeNameTag)
    t = parMatch.group(3)
  else:
    t = BeautifulSoup(rest).get_text()
  
 
  t, indexRefsTag = findSiehe(t)
  rest, ment = parseMentionings(soup, t)
  
  headerTag.append(rest)
  if ment:
    headerTag.append(ment)
  if indexRefsTag:
    headerTag.append(indexRefsTag)
    
  if header.get_text().strip() != headerTag.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    print('\n')

  return name.rstrip(', '), headerTag



####################### 3.1.3 Landmark Header ####################################

def landHeaderToXML(header):
  headerTag = soup.new_tag("landmark-header")
  geogTag = soup.new_tag("geogName")
  headerTag.append(geogTag)

  # Name
  name = header.b.get_text()
  nameTag = soup.new_tag("name")
  geogTag.append(nameTag)
  nameTag.append(name)
  
  # alternative names & mentionings
  ohneB = BeautifulSoup(str(header))
  ohneB.b.decompose()
  

  geogTag, ohneAddN = addNamesToXML(geogTag, unicode(ohneB))
  if ohneAddN:
    t = BeautifulSoup(ohneAddN).get_text()
  else:
    t = ohneB.get_text()

  headerTag.append(geogTag)

  text, indexRefsTag = findSiehe(t)
  t, ment = parseMentionings(soup, t)

  
  landkey = 'Fluss|Berg|gau[ ,]|Gau|Bach|Talschaft|Tal|Landschaft|Au|Waldung|Wald|Gemeindewald'
  landMatch = re.match('(.*)('+landkey+')(.*)', t)
  
  # oder gehoert goegFeat in goeogname??
  if landMatch:
    headerTag.append(landMatch.group(1))
    landtype = landMatch.group(2)
    geogTag["type"] = landtype
    headerTag.append(landtype)
    rest = landMatch.group(3)
  else:
    landkey += "|furt|berg"
    landNameMatch = re.search('(.*)('+landkey+')(.*)', name)
    if landNameMatch:
      landtype = landNameMatch.group(2)
      l = landtype.capitalize()
      geogTag["type"] = l
    else:
      geogTag["type"] = 'unknown'
    rest = t

  headerTag.append(rest)

  if ment:
    headerTag.append(ment)
  if indexRefsTag:
    headerTag.append(indexRefsTag)
  
  if header.get_text().strip() != headerTag.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    print('\n')
    
  return name.rstrip(', '), headerTag



####################### 3.1.4 Persongroup Header ####################################

def persGrHeaderToXML(header):
  headerTag = soup.new_tag("persongroup-header")
  
  text, indexRefsTag = findSiehe(header.get_text())
  # name + mentionings
  rest, ment = parseMentionings(soup, text)
  value = header.b.get_text() # sollte eigenlich nicht noetig sein, da name= value..
  name = rest
  grNameTag = soup.new_tag("group-name")
  headerTag.append(grNameTag)
  grNameTag.append(name)
  
  if ment:
    headerTag.append(ment)
  if indexRefsTag:
    headerTag.append(indexRefsTag)
  
  if header.get_text().strip() != headerTag.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    print('\n')

  return value.rstrip(', '), headerTag



####################### 3.1.5 Person Header ####################################

def persHeaderToXML(header):
  headerTag = soup.new_tag("person-header")
  persTag = soup.new_tag("person")
  headerTag.append(persTag)
  global person_id
  persTag['id'] = 'person_'+str(person_id)
  person_id += 1

  # Name
  name = header.b.get_text()
  nameTag = soup.new_tag("persName")
  
  # alternative names ???
  ohneB = BeautifulSoup(str(header))
  ohneB.b.decompose()
  
  text, indexRefsTag = findSiehe(header.get_text())
  text, ment = parseMentionings(soup, text)
  description, ment2 = parseMentionings(soup, ohneB.get_text())

  genNameKeys = "der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\.|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|Junior|Jr|Senior|Sr|der Junge|der Alte"
  roleKeys = "K.nig|Kaiser|Herzog|Graf|Hzg\.|Kg\.|Ks\.|Herzogin|Gf\.|dt\. Kg\. und r.m\. Ks\.|Gr.fin"
  
  with codecs.open("forenames.txt", "r", "utf-8") as file:
    matched = False
    forenameList = file.read().split('\n')
    forenameKeys = '|'.join(forenameList)
    
    # Fust von Diebach gen. Knebel
    surForeMatch = re.match('(?P<surname>[^, ]+?)(, )(?P<forename>'+forenameKeys+')([ von]*,? )' , text)
    foreMatch = re.match('(?P<forename>'+forenameKeys+')(,)' , text)
    foreSurMatch = re.match('(?P<forename>'+forenameKeys+')( )(?P<surname>[^,]+)(,)' , text)
    foreVonSurMatch = re.match('(?P<forename>[\w]+)( )(?P<surname>von [^,]+)(,)' , text)
    foreGenRoleMatch = re.match('(?P<forename>[\w]+)( )(?P<genName>'+genNameKeys+')(,? ?)(?P<roleName>'+roleKeys+'?)', text)
    foreGenMatch = re.match('(?P<forename>[\w]+)( )(?P<genName>'+genNameKeys+')', text)
    foreRoleMatch = re.match('(?P<forename>'+forenameKeys+')(, )(?P<roleName>'+roleKeys+')', text)
    
    for m in [foreGenRoleMatch, foreGenMatch, surForeMatch, foreVonSurMatch, foreRoleMatch, foreSurMatch, foreMatch]:
      if m and not matched:
        nameTag, index = annotateGrNames(m, nameTag)
        description = text[index:]
        matched = True
        break
  if not matched:
    nameTag.append(name)

  persTag.append(nameTag)
  
  if description:
    descriptionTag = soup.new_tag('description')
    persTag.append(descriptionTag)
    descriptionTag.append(description)

  if ment:
    headerTag.append(ment)
  if indexRefsTag:
    headerTag.append(indexRefsTag)
    
  if header.get_text().strip() != headerTag.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text() + '\n')
    
  return name.rstrip(', '), headerTag


############################## 3.2 Bodies ###########################

def relConcToXML(liste, prefix):
  #parst eine Liste von concepts
  relConcTag = soup.new_tag('related-concepts')  
  concList = []
  concTag = None
  for concHTML in liste:
    conc = BeautifulSoup(concHTML)
    einrueckMatch = re.match('( *?\-)(.*)', conc.get_text())
    if einrueckMatch:
      concList.append(einrueckMatch.group(2))
      continue
    elif concList:
      innerRelConcTag = relConcToXML(concList, prefix + ' -')
      if concTag:
        concTag.append(innerRelConcTag)
      else:
        concTag = innerRelConcTag
      concList = []
      
    concTag = soup.new_tag('concept')
    relConcTag.append(prefix)
    relConcTag.append(concTag)
    rest, ment = parseMentionings(soup, conc.get_text())
    nameTag = soup.new_tag('name')
    concTag.append(nameTag)
    nameTag.append(rest)
    if ment:
      concTag.append(ment)

  if concList:
      innerRelConcTag = relConcToXML(concList, prefix + ' -')
      if concTag:
        concTag.append(innerRelConcTag)
      else:
        concTag = innerRelConcTag
      if relConcTag:
        relConcTag.append(concTag)
    
  return relConcTag


######################## 3.2.1 ListingBody (FamilyBody, PersongroupBody) ##############

def listingBodyToXML(body):
  listBodyTag = soup.new_tag("listing-body")
  membersTag = soup.new_tag("members")
  listBodyTag.append(membersTag)

  personList = str(body).split("<br>") # personlist kann auch concepts enthalten
  concList = []
  hyp = ''
  personTag = None
  for personHTML in personList:
    person = BeautifulSoup(personHTML)
    
    einrueckMatch = re.match('( *?\-)(.*)', person.get_text())
    if einrueckMatch:
      concList.append(einrueckMatch.group(2))
      continue
      
    elif concList:
      relConcTag = relConcToXML(concList, ' -')
      if personTag:
        personTag.append(relConcTag)
      concList = []
  
    rest, ment = parseMentionings(soup, person.get_text())
    personAttrList = rest.split(",")
    personName=personAttrList[0]
    personTag = soup.new_tag('person')
    global person_id
    personTag['id'] = 'person_'+str(person_id)
    person_id += 1
    membersTag.append(personTag)
    nameTag = soup.new_tag("persName")
    personTag.append(nameTag)
    parsePersName(nameTag, personName)

    
    if personName:
      possForename = personName.split()[0].strip(' ()[].,;')
      if possForename != "siehe" and possForename != "Siehe" and possForename != 'Leibeigene' and possForename != 'Herrin' and possForename != "Rechtshandlung" and possForename != "Frau" and possForename != "Edelmann":
        if not possForename in forenames:
          forenames.append(possForename)
  

    attrs = ""
    if len(personAttrList)>1:
      possAddName = personAttrList[1]
      if re.match("[ ]"+"(gen\.|den man nennet|dem man sprichet)"+"(.+)",possAddName):
        nameTag.append(", ")
        parsePersName(nameTag, possAddName)
        personAttrList = personAttrList[1:]
    
    for attr in personAttrList[1:]:
      attrs = attrs + "," + attr

    persInfoTag = soup.new_tag('description')
    if attrs:
      personTag.append(persInfoTag)
      persInfoTag.append(attrs)
    
    if ment:
      personTag.append(ment)

 
  if body.get_text().strip() != listBodyTag.get_text().strip():
    print(body.get_text())
    print(listBodyTag.get_text() + '\n')
    
  return listBodyTag


############################ 3.2.2 RelatedConceptsBody (rest) ##############

def relConcBodyToXML(body):
  listBodyTag = soup.new_tag("concept-body")
  bodyList = str(body).split("<br>")

  if not body.get_text():
    return listBodyTag
  
  relTag = soup.new_tag("related-concepts")
  listBodyTag.append(relTag)
  concList = []
  conceptTag = None
  for conceptHTML in bodyList:
    concept = BeautifulSoup(conceptHTML)
    
    einrueckMatch = re.match('( *-)(.*)', concept.get_text())
    if einrueckMatch:
      if einrueckMatch.group(2).strip().startswith('-') and not concList:
        print einrueckMatch.group(2)
        raise ExtractorException('Ill-formed HTML (body): unexpected indentation level in inner related concept (too many \'-\')')
      concList.append(einrueckMatch.group(2))
      continue
      
    elif concList:
      relConcTag = relConcToXML(concList, ' -')
      conceptTag.append(relConcTag)
      concList = []
  
    rest, ment = parseMentionings(soup, concept.get_text())
    conceptTag = soup.new_tag('concept')
    relTag.append(conceptTag)
    nameTag = soup.new_tag('name')
    conceptTag.append(nameTag)
    nameTag.append(rest)
  
    if ment:
      conceptTag.append(ment)
 
  if concList:
      relConcTag = relConcToXML(concList, ' -')
      if conceptTag:
        conceptTag.append(relConcTag)
      else:
        raise ExtractorException('Ill-formed HTML (body): unexpected indentation level in related concept')
  
 
  if body.get_text().strip() != listBodyTag.get_text().strip():
    print(body.get_text())
    print(listBodyTag.get_text() + '\n')
    
  return listBodyTag


############################ 4. Parser ##############################

############################ 4.1 Familiy Parser  #####################

def famToXML(family, id):
  itemTag = soup.new_tag("item")
  value, itemHeader = famHeaderToXML(family.header)
  itemTag['id'] = 'item_'+str(id)
  itemTag['type'] = 'family'
  itemTag['value'] = value
  itemTag.append(itemHeader)
  itemBody = listingBodyToXML(family.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag


################## 4.2 PersongroupParser #############

def persGrToXML(persongroup, id):
  itemTag = soup.new_tag("item")
  value, itemHeader = persGrHeaderToXML(persongroup.header)
  itemTag['id'] = 'item_'+str(id)
  itemTag['type'] = 'persongroup'
  itemTag['value'] = value
  itemTag.append(itemHeader)
  itemBody = listingBodyToXML(persongroup.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
################## 4.3 PersonParser #############

def persToXML(person, id):
  itemTag = soup.new_tag("item")
  value, itemHeader = persHeaderToXML(person.header)
  itemTag['id'] = 'item_'+str(id)
  itemTag['type'] = 'person'
  itemTag['value'] = value
  itemTag.append(itemHeader)
  itemBody = relConcBodyToXML(person.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
################## 4.4 LocationParser #############

def locToXML(location, id):
  pass
  itemTag = soup.new_tag("item")
  value, itemHeader = locHeaderToXML(location.header)
  itemTag['id'] = 'item_'+str(id)
  itemTag['type'] = 'location'
  itemTag['value'] = value
  itemTag.append(itemHeader)
  itemBody = relConcBodyToXML(location.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
################## 4.5 LandmarkParser #############

def landToXML(landmark, id):
  itemTag = soup.new_tag("item")
  value, itemHeader = landHeaderToXML(landmark.header)
  itemTag.append(itemHeader)
  itemTag['id'] = 'item_'+str(id)
  itemTag['type'] = 'landmark'
  itemTag['value'] = value
  itemBody = relConcBodyToXML(landmark.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  


####################### 5. writing into files ###################


def writeHeaderText (liste, file):
  with open (file, 'w') as file:
    for item in liste:
      file.write(item.header.get_text().encode('utf-8') + "\n" + "\n")


def writeHeaderTexts ():
  writeHeaderText(locations, 'extractedLocationsRead5.txt')    
  writeHeaderText(families, 'extractedFamiliesRead5.txt')    
  writeHeaderText(landmarks, 'extractedLandmarksRead5.txt')    
  writeHeaderText(persons, 'extractedPersonsRead5.txt')    
  writeHeaderText(persongroups, 'extractedPersongroupsRead5.txt')    
  writeHeaderText(unclassified, 'extractedUnclassRead5.txt')    


def writeHeader(liste, funcToXML, file):
  with open (file, 'w') as file:
    for item in liste:
      x = funcToXML(item.header)
      file.write(str(x) + "\n")

def writeHeaders():
  writeHeader(persons, persHeaderToXML, 'persHeaderXML.xml')
  writeHeader(locations, locHeaderToXML, 'locHeaderXML.xml')
  writeHeader(families, famHeaderToXML, 'famHeaderXML.xml')
  writeHeader(landmarks, landHeaderToXML, 'landHeaderXML.xml')
  writeHeader(persongroups, persGrHeaderToXML, 'persGrHeaderXML.xml')


#################################################################################
########################## 6. index_to_xml  #######################################

def headBod(h, b, lineList):
  if len(lineList) > 0:
    firstLineText=BeautifulSoup(lineList[0]).get_text().strip()
    
    if firstLineText.startswith('siehe') or firstLineText.startswith('mit siehe'):
     h += lineList[0]
     lineList = lineList[1:]
     h, b = headBod(h, b, lineList)
     
    else:
      b = '<br>'.join(lineList)
  return (h, b)



def index_to_xml():
  '''
  Main function. Finds the index in html/sbr-regesten2.html, converts it into xml and writes it into index.xml.
  '''
  print('Item Extractor is working ..')
  text = ""
  t = ""

  with codecs.open("html/sbr-regesten2.html", "r", "cp1252") as f:
    text = f.read()
    text = unicode(text)
    t2 = text.replace("\n"," ")
    t = t2.replace("\r","")

  soup = BeautifulSoup(t)
  soup = preprocess(soup)
  print('preprocessing done!')

  indexTag = soup.new_tag('index')
  indexInfoTag = soup.new_tag('index-info')
  indexTag.append('Index \n')
  indexTag.append(indexInfoTag)

  items = []  # list of all items

  # header-body
  htmlItems = soup.findAll('p')
  
  foundIndex = False
  nextIndexInfo = False
  emptyCount = 0
  for htmlItem in htmlItems:
    if emptyCount >= 10 and foundIndex:
      break
    elif htmlItem.get_text().strip() == '' and foundIndex:
      emptyCount += 1
    else:
      emptyCount = 0
      if htmlItem.get_text().strip() == 'Index':
        foundIndex = True
        nextIndexInfo = True
       
      elif nextIndexInfo:
        indexInfoTag.append(htmlItem.get_text())
        indexInfoTag.append('\n')
        nextIndexInfo = False
        continue

      if foundIndex:
        s = unicode(htmlItem)

        lineList = s.split('<br>')
        h = lineList[0]
        b = ''
        restList = lineList[1:]
        
        h,b = headBod(h,b,restList)

        h = '<itemHeader>'+h+'</itemHeader>'
        b = '<itemBody>'+b+'</itemBody>'
        header = BeautifulSoup(h)
        body = BeautifulSoup(b)
        item = IndexItem(header, body)
        items.append(item)

  print("ItemClassifier and ItemExtractor is processing..")

  xmlItems = []
  id = -1

  for item in items:
    header = item.header.get_text()
    
    famMatch = re.search('[Ff]amilie|Adelsgeschlecht', header)
    
    locMatch = re.search('[Ss]tadt,|Stadtteil|Dorf|Burg |Hof |Hofgut|Gemeinde |Ort |.rtlichkeit |Kloster|Abtei|Schloss|Herrschaft|Gft\.|Kgr\.|Region|Gebiet|Land |Kgr\.|Herzogtum|Hzgt\.|[Gg]rafschaft|F.rstentum|Deutschordenskommende|RLP|Gde\.|Bistum|Vogtei|Regierungssitz|Hochstift|Pfarrei|W.stung|F\)|Erzstift|, Erzbistum|Dekanat|Domstift|Reichsland|Deutschordensballei|M.hle|Wallfahrt|Land |Reise|lothr. Amt|Deutschordenshaus|[Ss]tadt (?!S)', header)
    
    grpMatch = re.search('Notare|, Grafen|, Markgrafen|[Hh]erz.ge|[Bb]isch.fe|Edelknechte|K.nige|[Ff].rsten|Personen|Herren|Ritter von|Einwohner|P.pste|Wildgrafen|Herrn von|(?<!, )Dominikaner', header)
    
    persMatch = re.search('Bischof|Pastor|Graf |Papst |II\.|I\.|III\.|IV\.|V\.|Hzg\.|Bf\.|Adliger|Herr |Frau |Kg\.|Elekt|meister|Ritter|, Schulthei.|, Herzogin|Amtmann|Lehensmann|Vetter von|Markgraf |Pfalzgraf|Ebf\.|, Herzog|, Dominikaner|Erzpriester|[dD]iakon|Provinzial|r.m\. K.nig|Kammermajor|Witwe|Junker|Stephan|Jacob|Klaus|Elisabeth|Fabricio|Nikolaus|Hans|Alheim|Gerbod', header)
    
    landMatch = re.search('Fluss|Berg|gau[ ,]|Gau|Bach|Tal|Landschaft|Wald|Waldung|Gemeindewald|Au|furt|Engenberg', header)
    
    sieheMatch = re.search('siehe', header)
    
    if famMatch:
      x = famToXML(item, id)
      xmlItems.append(x)
      families.append(item)

    elif locMatch:
      pass
      x = locToXML(item, id)
      xmlItems.append(x)
      locations.append(item)

    elif grpMatch:
      x = persGrToXML(item, id)
      xmlItems.append(x)  
      persongroups.append(item)

    elif persMatch:
      x = persToXML(item, id)
      xmlItems.append(x)
      persons.append(item)

    elif landMatch:
      x = landToXML(item, id)
      xmlItems.append(x)
      landmarks.append(item)

    elif sieheMatch:
      siehe.append(id)
      item.header['tmp_id'] = id
      xmlItems.append(item)
      
    else:
      unclassified.append(item)
    
    id += 1

    
  xmlItemsComplete = []
  for item in xmlItems:
    if not isinstance(item, IndexItem):
      xmlItemsComplete.append(item)
    else:
      type = None
      line = item.header.get_text()
      sieheMatch = re.search('siehe (.*)',line)
      if sieheMatch:
        n = sieheMatch.group(1).strip()
        itemTag = soup.new_tag("item")
        for i in xmlItems:
          if not isinstance(i, IndexItem):
            if n in i['value'].strip():
              type = i['type']
              itemTag['type'] = type
              itemTag['value'] = item.header.b.get_text()
              itemTag['id'] = 'item_'+str(item.header['tmp_id'])
              if not type:
                print (value+" konnte nicht aufgeloest werden!?!")
                
              if type == 'location':
                settleType = i.find('location-header').placeName.settlement['type']
                value, header = locHeaderToXML(item.header)
                header.placeName.settlement['type'] = settleType
                itemTag.append(header)
                
              if type == 'family':
                value, header = famHeaderToXML(item.header)
                itemTag.append(header)

              xmlItemsComplete.append(itemTag)
              break


  print("Items classified")  
  print("Familien: "+ str(len(families)))
  print ("Unclassified: "+ str(len(unclassified)))
  print("Persons: " + str(len(persons)))
  print("Landmarks: " + str(len(landmarks)))
  print("Personengruppen: " + str(len(persongroups)))
  print("Locations: " + str(len(locations)))
  print("Siehe: " + str(len(siehe)))



  with open ('index20.xml', 'w') as file:
    for item in xmlItemsComplete:
      indexTag.append(item)
      indexTag.append('\n')
    file.write(indexTag.encode('utf-8'))
  print ("index.xml ausgegeben")
     
  with open ('prettyXmlItems.xml', 'w') as file:
    for item in xmlItemsComplete:
      file.write(item.encode('utf-8') + "\n")

  with open ('extractedItems.txt', 'w') as file: #
    file.write(str(items))
    
  writeHeaders()
  writeHeaderTexts()
  print('Itmes extracted')


  # legt mit forenames.txt eine Datei mit Vornamen an
  with codecs.open ('forenames2.txt', 'w', "utf-8") as file:
    file.write('\n'.join(forenames))

  print ('Forenames.txt angelegt. Anzahl der Vornamen: '+str(len(forenames)))


'''if __name__ == 'main':
  index_to_xml()'''
  