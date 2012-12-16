# 15-12-2012 Susanne Fertmann


from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys

sys.setrecursionlimit(10000)


soup=BeautifulSoup()
forenames=[]
persons=[]
persongroups=[]
locations=[]
landmarks=[]
unclassified=[]
families=[]
siehe=[] # to collect items that will be classified later through their reference with "siehe"

########################## 1. Preprocessing ########################

def delSpan(s):
  s=re.sub('\</?span.*?\>','',s)
  return s
  
def joinb (s):
  s=re.sub('(?u)(\</b\>)([(:?\<.*?\>), ]*)(\<b\>)','\g<2>', s)
  return s
  
def joini (s):
  s=re.sub('(?u)(\</i\>)([(:?\<.*?\>), ]*)(\<i\>)','\g<2>', s)
  return s
  
def preprocess(soup):
  print("preprocessing..")
  s=unicode(soup)
  s=delSpan(s)
  s=joinb(s)
  s=joini(s)
  soup=BeautifulSoup(s)
  return soup


########################## 2. ItemExtractor ########################

class IndexItem:
  def __init__(self, header, body):
    self.header = header
    self.body = body
  def __repr__(self):
    return (str(self.header)+"\n"+str(self.body))+"\n"+"\n"



#########################################################################################################################
###############################################   3. ITEMPARSER   #######################################################
#########################################################################################################################


# to parse (find and tag) the mentionings in the headers
def parseMentionings(soup, t):
  mentioningsTag=None
  text=t
  mentionings=[]
  ment='((?:\[?\+\]? )?[01][0-9][0-9][0-9]\-?\/?[01]?[0-9]?\-?[0-3]?[0-9]? ?\([a-f]?k?u?r?z? ??n?a?c?h?v?o?r?n?t?e?u?m?p?o?s?t?\??\.?\) ?)( Anm\.)?|((?:\[?\+\]? )?[01][0-9][0-9][0-9]\-?[01]?[0-9]?\-?[0-3]?[0-9]? ?\(?z?w?i?s?c?h?e?n?\)?)'
  #1306-03-24 (?), 1504/1505 (a) Anm., 1431-1459 (zwischen)
  
  mentMatch=re.match('(.*?)('+ment+',? ?)$', text)
  while mentMatch:
    text= mentMatch.group(1)
    menti=mentMatch.group(2)
    mentionings.insert(0, menti)
    mentMatch=re.match('(.*?)('+ment+'),\.? $', text)
  
  if mentionings:
    mentioningsTag = soup.new_tag("mentioned-in")
    notFirstEl=False
    for reg_ref in mentionings:
      if notFirstEl:
        mentioningsTag.append(', ')
      else:
        notFirstEl=True
      reg_refTag = soup.new_tag("reg-ref")
      reg_refTag.append(reg_ref)
      mentioningsTag.append(reg_refTag)
  return (text, mentioningsTag)


def addNamesToXML(parentTag, text):
  #print('\n')
  #print('addNames erreicht: '+ text)
  #altNMatch=re.match(r"(.*?)\(.*?<i(?: .*)?>(?:.*[a-z]+.*)<.i>(?:.*\), .*)", text)
  #altNMatch=re.match("(?u)(.*?\(.*\<i(?: .*)?\>)(.*[a-z]+.*)(.*\))(.*?, .*)", text)
  altNMatch=re.match("(?u)(.*?\(\<i.*?\>)(.*?)\)(.*, .*)", text)
  r=None
  # alternative names
  if altNMatch:
    #print('gematched')
    altNames=BeautifulSoup(altNMatch.group(2)).get_text().strip().split(',') #TODO
    #print altNames
    #print ('altNames: '+ str(altNames))
    addNamesTag = soup.new_tag("addNames")
    addNamesTag.append(BeautifulSoup(altNMatch.group(1)).get_text())

    parentTag.append(addNamesTag)
    #addNamesTag.append(' (')
    notFirstEl=False
    for altName in altNames:
      if notFirstEl:
         addNamesTag.append(',')
      else:
        notFirstEl=True
      addNameTag = soup.new_tag("addName")
      addNameTag.append(altName)
      addNamesTag.append(addNameTag)
    addNamesTag.append('')
    addNamesTag.append(')')
    r=altNMatch.group(3)
  #print (parentTag)
  #print (r)
  return (parentTag, r)


def parsePersName (nameTag, personName):
  foreTag=soup.new_tag("forename")
  
  genNameKeys="der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\.|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|Junior|Jr|Senior|Sr|der Junge|der Alte"
  genNameMatch=re.search("(.*?)(\[?"+genNameKeys+"\]?)(.*)",personName)
  
  #addNameKeys="gen\.|den man nennet|dem man sprichet"
  addNameMatch=re.search("(.*?)"+"(gen\.|den man nennet|dem man sprichet)"+"(.+)",personName)
  
  #print(personName)
  if genNameMatch:
    foreName=genNameMatch.group(1)
    if foreName.strip()!= "":
      nameTag.append(foreTag)   
      foreTag.append(foreName) 
    genName=genNameMatch.group(2)
    restName=genNameMatch.group(3)
    genNameTag=soup.new_tag("genName")
    nameTag.append(genNameTag)
    genNameTag.append(genName)   
    nameTag.append(restName)
  #print(personName)
    
  elif addNameMatch:
    foreName=addNameMatch.group(1)
    gen=addNameMatch.group(2)
    addName=addNameMatch.group(3)
    if foreName.strip()!= "":
      nameTag.append(foreTag)   
      foreTag.append(foreName) 
    addNamesTag=soup.new_tag("addNames")
    addNameTag=soup.new_tag("addName")
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
    matchDict=match.groupdict()
    for groupName in matchDict.keys():
      if equalMatchGroup(match,i,groupName):
        return groupName
    return None
    
def annotateGrNames(m, nameTag):
  for i in range(1,len(m.groups())+1):
    label=getMatchLabel(m,i)
    if label and m.group(i):
      labelTag= soup.new_tag(label)
      nameTag.append(labelTag)
      labelTag.append(m.group(i))
    else:
      nameTag.append(m.group(i))
  return nameTag, m.end(m.lastindex)


####################### 3.1. Header Parser ####################################

####################### 3.1.1 LocationHeader ####################################

def locHeaderToXML(header):
  headerTag = soup.new_tag("location-header")
  placeNameTag = soup.new_tag("placeName")

  # Wuestungen
  settleTag = soup.new_tag("settlement")
  placeNameTag.append(settleTag)
 
  wuestMatch=re.search('(Staerk, W.stungen Nr. [0-9][0-9]?)', header.get_text())
  w=False
  if wuestMatch:
    w=True      
    w_ref=wuestMatch.group(0)
    settleTag["w-ref"]=w_ref
  settleTag["w"]=w
 
  # Settlement name 
  name = header.b.get_text()
  settleTag.append(name)
  
  ohneB= BeautifulSoup(str(header))
  ohneB.b.decompose()
  rest=ohneB
  
  
  # SettlementType, RefPoint, District, Region, Country
  settlement="Dorf|Stadt|Stadtteil|Burgsiedlung|Burg|ehem. Burg|Hofgut|Hof|Ort|.rtlichkeit|Gemeinde|Kloster|Abtei|Schloss|Herrschaft|Gft\.|Kgr\.|Land|Kgr\.|Herzogtum|Hzgt\.|Grafschaft|F.rstentum|Deutschordenskommende|Bistum|Vogtei|Regierungssitz|Hochstift|Pfarrei|Erzstift|Erzbistum|Dekanat|Domstift|Reichsland|Deutschordensballei|\w*abtei|Wasserburg|M.hle|Zisterzienserabtei|Region"
  districtKeys="Gem|Stadtverband [^;,]+|Gde. Bliesmengen-Bolchen|Gde\. [^,;]+|[\w-]+-Kreis|Kr\. [^,;]+|[-\w]+kreis|Stadt [\w][\w]\.|Stadt [\w-]+|Kreis [^;,]+"
  district= "(?:"+districtKeys + ")(?:, (?:" + districtKeys + "))?"
  regionKeys="Dep\.,? [A-Za-z-]+|SL|NRW|By|RLP|BW|Prov\..+|Hessen"
  country="B|F|NL|CH|Lux|It|L|Spanien|T.rkei"
  settlementKeys="(?:"+settlement+")(?![\w])"
  #settlementKeys="(?:"+settlement+")(?:"+settlement+")(?![\w])"
  countryKeys="(?:"+country+")(?![\w])"
  
  #print(text)
  placeNameTag, ohneAddN=addNamesToXML(placeNameTag, unicode(rest))
  #print (placeNameTag)
  
  if ohneAddN:
    text=BeautifulSoup(ohneAddN).get_text()
  else:
    text=rest.get_text()
  #placeNameTag.append(', ')  
  #print(text)
  
  
  # Mentionings
  text, ment = parseMentionings(soup, text)
  
  settleMatch=re.match('(?u)(.*?)('+ settlementKeys +')(.*?)', text)
  
  if settleMatch:
    placeNameTag, index = annotateGrNames(settleMatch, placeNameTag)
    text=text[index:]
    #print(text)
    settleTag["type"]=settleMatch.group(2)
  else:
    settleTag["type"]='unknown'
    #text=text.lstrip(',')
  
  
  distRegMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district + ')(.*)(?P<region>'+ regionKeys + ')(.*)', text)
  distRegCountMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district +')(.*)(?P<region>'+ regionKeys + ')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  distCountMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district +')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  regCountMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<region>'+ regionKeys + ')(.*)(?P<country>' + countryKeys + ')(.*)', text)
  countMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<country>'+ countryKeys + ')(.*)', text)
  regMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<region>'+ regionKeys + ')(.*)', text)
  distMatch=re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)([^\w-]+|[^\w]+W.stung.*?[^\w]+)(?P<district>'+ district + ')(.*)', text)
  settleMatch=re.match('(?u)([^\w]?(?:siehe [\w/-]+)?)(?P<referencePoint>[\w\.\/ -]*?)(.*)', text)
  
  possibleMatches = [distRegCountMatch, distRegMatch, distCountMatch,  regCountMatch, regMatch, distMatch, countMatch, settleMatch]
  for m in possibleMatches:
    if m:
      placeNameTag, index = annotateGrNames(m, placeNameTag)
      
      if "region" in m.groupdict():   
        region=m.group("region")
        if "Prov" in region:
          placeNameTag.find("region")['type'] = 'Provinz'
        elif "Dep" in region:
          placeNameTag.find("region")['type'] = 'Departement'
        elif "NRW" or "SL" or "RLP" or "By" or "BW" or "Hessen" in region:
          placeNameTag.find("region")['type'] = 'Bundesland'
          
      break

  #print (placeNameTag)
  
  headerTag.append(placeNameTag)
  
  
  if ment:
    headerTag.append(ment)
  
  #print (headerTag)

  
  '''
  mentionings=re.findall('[1][0-9][0-9][0-9]\-[01][0-9]\-[0-3][0-9] ?\(?[a-d]?n?a?c?h?v?o?r?\)?|[1][0-9][0-9][0-9] ?\(?[a-d]?n?a?c?h?v?o?r?\)?', header.get_text())
  '''

  return name.rstrip(', '), headerTag


####################### 3.1.2 Family Header ####################################

def famHeaderToXML(header):
  headerTag = soup.new_tag("family-header")

  # Name
  name = header.b.get_text()
  famNameTag=soup.new_tag('family-name')
  headerTag.append(famNameTag)
  nameTag=soup.new_tag('name')
  famNameTag.append(nameTag)
  nameTag.append(name)
  ohneB= BeautifulSoup(str(header))
  ohneB.b.decompose()
  
  # rest + mentionings
  rest, ment = parseMentionings(soup, ohneB.get_text())

  # Alternative names & locations (both are in parentesis right after the name, alternative names are in italics, locations not)
  parMatch=re.match(r"(.*?)\((.*[A-Za-z][a-z][a-z][a-z].*)(\), .*)", rest)
  famNameTag, rx=addNamesToXML(famNameTag, rest)

  if rx:
    r=rx
  # location  
  elif parMatch:
    headerTag.append(BeautifulSoup(parMatch.group(1)).get_text())
    loc =BeautifulSoup(parMatch.group(2)).get_text().strip()
    locTag = soup.new_tag("location")
    headerTag.append('(')
    headerTag.append(locTag)
    locTag.append(loc)
    headerTag.append('')
    r=parMatch.group(3)
  else:
    r=rest
  
  #append mentionings
  headerTag.append(r)
  if ment:
    headerTag.append(ment)

  '''if headerTag.get_text().strip() != header.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    #print(rest.get_text())
    print(headerTag)
    print('\n')'''
  return name.rstrip(', '), headerTag



####################### 3.1.3 Landmark Header ####################################

def landHeaderToXML(header):
  headerTag = soup.new_tag("landmark-header")
  geogTag= soup.new_tag("geogName")
  headerTag.append(geogTag)

  # Name
  name = header.b.get_text()
  nameTag= soup.new_tag("name")
  geogTag.append(nameTag)
  nameTag.append(name)
  
  # alternative names & mentionings
  ohneB= BeautifulSoup(str(header))
  ohneB.b.decompose()
  
  ohneMent, ment = parseMentionings(soup, ohneB.get_text())
  #print(ohneMent)
  
  headerTag, ohneAddN=addNamesToXML(headerTag, unicode(ohneMent))
  if ohneAddN:
    #print(ohneAddN)
    t=BeautifulSoup(ohneAddN).get_text()
  else:
    t=ohneMent

  landkey='Fluss|Berg|gau[ ,]|Gau|Bach|Talschaft|Tal|Landschaft|Au|Wald|Waldung|Gemeindewald'
  landMatch= re.search('('+landkey+')(.*)', t)
  
  if landMatch:
    landtype =landMatch.group(1)
    geogTag["type"]=landtype
    geogFTag=soup.new_tag('geogFeat')
    headerTag.append(', ')
    headerTag.append(geogFTag)
    geogFTag.append(landtype)
    rest= landMatch.group(2)
  else:
    landkey+="|furt|berg"
    landNameMatch= re.search('(.*)('+landkey+')(.*)', name)
    if landNameMatch:
      landtype =landNameMatch.group(2)
      l=landtype.capitalize()
      geogTag["type"]=l
    else:
      geogTag["type"]='unknown'
    rest=t
  
  headerTag.append(rest)

  if ment:
    headerTag.append(ment)
  
  '''if itemHeader.get_text().strip() != header.get_text().strip():
    print(header.get_text())
    print(itemHeader.get_text())
    #print(rest.get_text())
    print(itemHeader)
    print('\n')'''
  return name.rstrip(', '), headerTag



####################### 3.1.4 Persongroup Header ####################################

def persGrHeaderToXML(header):
  headerTag = soup.new_tag("persongroup-header")
  
  # name + mentionings
  rest, ment = parseMentionings(soup, header.get_text())
  value= header.b.get_text() # sollte eigenlich nicht noetig sein, da name= value..
  name = rest
  grNameTag= soup.new_tag("group-name")
  headerTag.append(grNameTag)
  grNameTag.append(name)
  
  if ment:
    headerTag.append(ment)
  
  '''if headerTag.get_text().strip() != header.get_text().strip():
    print(header.get_text())
    print(headerTag.get_text())
    print(headerTag)
    print('\n')'''
  return value.rstrip(', '), headerTag



####################### 3.1.5 Person Header ####################################

def persHeaderToXML(header):
  headerTag = soup.new_tag("person-header")
  persTag= soup.new_tag("person")
  headerTag.append(persTag)

  # Name
  name = header.b.get_text()
  nameTag= soup.new_tag("persName")
  
  # alternative names ???
  rest1= BeautifulSoup(str(header))
  rest1.b.decompose()
  
  # description + mentionings
  description, ment = parseMentionings(soup, rest1.get_text())
  
  #
  text, ment2 = parseMentionings(soup, header.get_text())
  genNameKeys="der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\.|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\.|Junior|Jr|Senior|Sr|der Junge|der Alte"
  roleKeys="K.nig|Kaiser|Herzog|Graf|Hzg\.|Kg\.|Ks\.|Herzogin|Gf\.|dt\. Kg\. und r.m\. Ks\.|Gr.fin"
  
  with codecs.open("forenames.txt", "r", "utf-8") as file:
    matched=False
    forenameKeys=file.read()
    
    # Fust von Diebach gen. Knebel
    
    #print(forename)
    surForeMatch=re.match('(?P<surname>[^, ]+?)(, )(?P<forename>'+forenameKeys+')([ von]*,? )' , text)
    foreMatch=re.match('(?P<forename>'+forenameKeys+')(,)' , text)
    foreSurMatch=re.match('(?P<forename>'+forenameKeys+')( )(?P<surname>[^,]+)(,)' , text)
    foreVonSurMatch=re.match('(?P<forename>[\w]+)( )(?P<surname>von [^,]+)(,)' , text)
    foreGenRoleMatch=re.match('(?P<forename>[\w]+)( )(?P<genName>'+genNameKeys+')(,? ?)(?P<roleName>'+roleKeys+'?)', text)
    foreGenMatch=re.match('(?P<forename>[\w]+)( )(?P<genName>'+genNameKeys+')', text)
    foreRoleMatch=re.match('(?P<forename>'+forenameKeys+')(, )(?P<roleName>'+roleKeys+')', text)
    
    for m in [foreGenRoleMatch, foreGenMatch, surForeMatch, foreVonSurMatch, foreRoleMatch, foreSurMatch, foreMatch]:
      if m and not matched:
        nameTag, index=annotateGrNames(m, nameTag)
        description=text[index:]
        matched=True
        break
  if not matched:
    nameTag.append(name)

  persTag.append(nameTag)
  
  if description:
    descriptionTag=soup.new_tag('description')
    persTag.append(descriptionTag)
    descriptionTag.append(description)

  if ment:
    headerTag.append(ment)
    
  '''if itemHeader.get_text().strip() != header.get_text().strip():
    print(header.get_text())
    print(itemHeader.get_text())
    print(itemHeader)
    print('\n')'''
  return name.rstrip(' ,'), headerTag


############################## 3.2 Bodies ###########################

def relConcToXML(liste, prefix):
  #parst eine Liste von concepts
  relConcTag=soup.new_tag('related_concepts')  
  concList=[]
  concTag=None
  for concHTML in liste:
    conc = BeautifulSoup(concHTML)
    einrueckMatch=re.match('( *?\-)(.*)', conc.get_text())
    if einrueckMatch:
      concList.append(einrueckMatch.group(2))
      continue
    elif concList:
      innerRelConcTag=relConcToXML(concList, prefix + ' -')
      if concTag:
        concTag.append(innerRelConcTag)
      else:
        concTag= innerRelConcTag
      concList=[]
      
    concTag=soup.new_tag('concept')
    relConcTag.append(prefix)
    relConcTag.append(concTag)
    rest, ment = parseMentionings(soup, conc.get_text())
    nameTag=soup.new_tag('name')
    concTag.append(nameTag)
    nameTag.append(rest)
    if ment:
      concTag.append(ment)

  if concList:
      innerRelConcTag=relConcToXML(concList, prefix + ' -')
      if concTag:
        concTag.append(innerRelConcTag)
      else:
        concTag= innerRelConcTag
      if relConcTag:
        relConcTag.append(concTag)
    
  return relConcTag


######################## 3.2.1 ListingBody (FamilyBody, PersongroupBody) ##############

def listingBodyToXML(body):
  listBodyTag = soup.new_tag("listing-body")
  membersTag = soup.new_tag("members")
  listBodyTag.append(membersTag)

  personList=str(body).split("<br>") # personlist kann auch concepts enthalten
  concList=[]
  hyp=''
  personTag=None
  for personHTML in personList:
    person = BeautifulSoup(personHTML)
    
    einrueckMatch=re.match('( *?\-)(.*)', person.get_text())
    if einrueckMatch:
      concList.append(einrueckMatch.group(2))
      continue
      
    elif concList:
      #print(concList)
      relConcTag=relConcToXML(concList, ' -')
      if personTag:
        personTag.append(relConcTag)
      concList=[]
  
    rest, ment = parseMentionings(soup, person.get_text())
    personAttrList=rest.split(",")
    personName=personAttrList[0]
    personTag=soup.new_tag('person')
    membersTag.append(personTag)
    nameTag=soup.new_tag("persName")
    personTag.append(nameTag)
    parsePersName(nameTag, personName)

    
    if personName:
      possForename= personName.split()[0].strip(' ()[].,;')
      if possForename != "siehe" and possForename != "Siehe" and possForename != 'Leibeigene' and possForename != 'Herrin' and possForename != "Rechtshandlung" and possForename != "Frau" and possForename != "Edelmann":
        if not possForename in forenames:
          forenames.append(possForename)
  

    attrs=""
    if len(personAttrList)>1:
      possAddName=personAttrList[1]
      #print(possAddName)
      if re.match("[ ]"+"(gen\.|den man nennet|dem man sprichet)"+"(.+)",possAddName):
        nameTag.append(", ")
        parsePersName(nameTag, possAddName)
        personAttrList=personAttrList[1:]
    
    for attr in personAttrList[1:]:
      attrs = attrs + "," + attr

    persInfoTag=soup.new_tag('description')
    if attrs:
      personTag.append(persInfoTag)
      persInfoTag.append(attrs)
    
    if ment:
      personTag.append(ment)
 
  '''if listBodyTag.get_text().strip() != body.get_text().strip():
    print(body.get_text())
    print(listBodyTag.get_text())
    #print(rest.get_text())
    print(listBodyTag)
    print('\n')'''
  return listBodyTag


############################ 3.2.2 RelatedConceptsBody (rest) ##############
# TODO: Namen anpassen

def relConcBodyToXML(body):
  listBodyTag = soup.new_tag("concept-body")
  personList=str(body).split("<br>") # personlist kann auch concepts enthalten

  if not body.get_text():
    return listBodyTag
  
  membersTag = soup.new_tag("related_concepts")
  listBodyTag.append(membersTag)
  concList=[]
  personTag=None
  for personHTML in personList:
    person = BeautifulSoup(personHTML)
    
    einrueckMatch=re.match('( *\-)(.*)', person.get_text())
    if einrueckMatch:
      concList.append(einrueckMatch.group(2))
      continue
      
    elif concList:
      relConcTag=relConcToXML(concList, ' -')
      personTag.append(relConcTag)
      concList=[]
  
    rest, ment = parseMentionings(soup, person.get_text())
    personTag=soup.new_tag('concept')
    membersTag.append(personTag)
    nameTag = soup.new_tag('name')
    personTag.append(nameTag)
    nameTag.append(rest)
  
    if ment:
      personTag.append(ment)
 
  if concList:
      #print (concList)
      relConcTag=relConcToXML(concList, ' -')
      if personTag:
        personTag.append(relConcTag)
  
 
  '''if listBodyTag.get_text().strip() != body.get_text().strip():
    print(body.get_text())
    print(listBodyTag.get_text())
    #print(rest.get_text())
    print(listBodyTag)
    print('\n')'''
  return listBodyTag


############################ 4. Parser ##############################

############################ 4.1 Familiy Parser  #####################

def famToXML(family, id):
  itemTag = soup.new_tag("indexItem")
  value, itemHeader=famHeaderToXML(family.header)
  itemTag['id']='item_'+str(id)
  itemTag['type']='family'
  itemTag['value']=value
  itemTag.append(itemHeader)
  itemBody=listingBodyToXML(family.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
'''def parseFamilies(families):
  with open ('families.xml', 'w') as file:
    for family in families:
      x= famToXML(family)
      file.write(str(x) + "\n")'''

################## 4.2 PersongroupParser #############

def persGrToXML(persongroup, id):
  itemTag = soup.new_tag("indexItem")
  value, itemHeader=persGrHeaderToXML(persongroup.header)
  itemTag['id']='item_'+str(id)
  itemTag['type']='persongroup'
  itemTag['value']=value
  itemTag.append(itemHeader)
  itemBody=listingBodyToXML(persongroup.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
'''def parsePersongroups(persongroups):
  with open ('persongroups.xml', 'w') as file:
    for persongroup in persongroups:
      x= persGrToXML(persongroup)
      file.write(str(x) + "\n")'''

################## 4.3 PersonParser #############

def persToXML(person, id):
  itemTag = soup.new_tag("indexItem")
  value, itemHeader=persHeaderToXML(person.header)
  itemTag['id']='item_'+str(id)
  itemTag['type']='person'
  itemTag['value']=value
  itemTag.append(itemHeader)
  itemBody=relConcBodyToXML(person.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
'''def parsePersons(persons):
  with open ('persons.xml', 'w') as file:
    for person in persons:
      x= persToXML(person)
      file.write(str(x) + "\n")'''


################## 4.4 LocationParser #############

def locToXML(location, id):
  itemTag = soup.new_tag("indexItem")
  value, itemHeader=locHeaderToXML(location.header)
  itemTag['id']='item_'+str(id)
  itemTag['type']='location'
  itemTag['value']=value
  itemTag.append(itemHeader)
  itemBody=relConcBodyToXML(location.body)
  itemTag.append(itemBody)
  print(value)
  return itemTag
  
  
'''def parseLocations(locations):
  with open ('locations.xml', 'w') as file:
    for location in locations:
      x= locToXML(location)
      file.write(str(x))
      file.write("\n")'''
      
################## 4.5 LandmarkParser #############

def landToXML(landmark, id):
  itemTag = soup.new_tag("indexItem")
  value, itemHeader=landHeaderToXML(landmark.header)
  itemTag.append(itemHeader)
  itemTag['id']='item_'+str(id)
  itemTag['type']='landmark'
  itemTag['value']=value
  itemBody=relConcBodyToXML(landmark.body)
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
      x= funcToXML(item.header)
      file.write(str(x) + "\n")

def writeHeaders():
  writeHeader(persons, persHeaderToXML, 'persHeaderXML.xml')
  writeHeader(locations, locHeaderToXML, 'locHeaderXML.xml')
  writeHeader(families, famHeaderToXML, 'famHeaderXML.xml')
  writeHeader(landmarks, landHeaderToXML, 'landHeaderXML.xml')
  writeHeader(persongroups, persGrHeaderToXML, 'persGrHeaderXML.xml')


#################################################################################
########################## 6. index_to_xml  #######################################


def index_to_xml():
  
  text=""
  t=""

  with codecs.open("index_n_mod_kurz.htm", "r", "utf-8") as f:
    text=f.read()
    t=text.replace("\n"," ")

  soup = BeautifulSoup(t)
  soup=preprocess(soup)
  print('preprocessing done!')

  items=[]  # list of all items

  # header-body
  htmlItems=soup.findAll('p')
  for htmlItem in htmlItems:
    s=str(htmlItem)
    pMatch=re.search('<p.*?>(.*)<.p.*?>', s)
    s=pMatch.group(1)
    brMatch=re.search('(.*?)<br>(.*)', s)
    if brMatch:
      h=brMatch.group(1)
      b=brMatch.group(2)
    else:
      h=s
      b=""
    h='<itemHeader>'+h+'</itemHeader>'
    b='<itemBody>'+b+'</itemBody>'
    header=BeautifulSoup(h)
    body=BeautifulSoup(b)
    item=IndexItem(header, body)
    items.append(item)

  print("ItemClassifier and ItemExtractor is processing..")

  xmlItems=[]
  id=0

  for item in items:
    header=item.header.get_text()
    
    famMatch=re.search('[Ff]amilie|Adelsgeschlecht', header)
    
    locMatch=re.search('[Ss]tadt,|Stadtteil|Dorf|Burg |Hof |Hofgut|Gemeinde |Ort |.rtlichkeit |Kloster|Abtei|Schloss|Herrschaft|Gft\.|Kgr\.|Region|Gebiet|Land |Kgr\.|Herzogtum|Hzgt\.|[Gg]rafschaft|F.rstentum|Deutschordenskommende|RLP|Gde\.|Bistum|Vogtei|Regierungssitz|Hochstift|Pfarrei|W.stung|F\)|Erzstift|, Erzbistum|Dekanat|Domstift|Reichsland|Deutschordensballei|M.hle|Wallfahrt|Land |Reise|lothr. Amt|Deutschordenshaus|[Ss]tadt (?!S)', header)
    
    grpMatch=re.search('Notare|, Grafen|, Markgrafen|[Hh]erz.ge|[Bb]isch.fe|Edelknechte|K.nige|[Ff].rsten|Personen|Herren|Ritter von|Einwohner|P.pste|Wildgrafen|Herrn von|(?<!, )Dominikaner', header)
    
    persMatch= re.search('Bischof|Pastor|Graf |Papst |II\.|I\.|III\.|IV\.|V\.|Hzg\.|Bf\.|Adliger|Herr |Frau |Kg\.|Elekt|meister|Ritter|, Schulthei.|, Herzogin|Amtmann|Lehensmann|Vetter von|Markgraf |Pfalzgraf|Ebf\.|, Herzog|, Dominikaner|Erzpriester|[dD]iakon|Provinzial|r.m\. K.nig|Kammermajor|Witwe|Junker|Stephan|Jacob|Klaus|Elisabeth|Fabricio|Nikolaus|Hans|Alheim|Gerbod', header)
    
    landMatch= re.search('Fluss|Berg|gau[ ,]|Gau|Bach|Tal|Landschaft|Wald|Waldung|Gemeindewald|Au|furt|Engenberg|berg', header)
    
    sieheMatch= re.search('siehe', header)
    
    #print(header)
    
    if famMatch:
      x=famToXML(item, id)
      xmlItems.append(x)
      families.append(item)

    elif locMatch:
      x=locToXML(item, id)
      xmlItems.append(x)
      locations.append(item)

    elif grpMatch:
      x=persGrToXML(item, id)
      xmlItems.append(x)  
      persongroups.append(item)

    elif persMatch:
      x=persToXML(item, id)
      xmlItems.append(x)
      persons.append(item)

    elif landMatch:
      x=landToXML(item, id)
      xmlItems.append(x)
      landmarks.append(item)

    elif sieheMatch:
      siehe.append(id)
      item.header['tmp_id']=id
      xmlItems.append(item)
      
    else:
      unclassified.append(item)
    
    id=id+1

    
  xmlItemsComplete=[]
  for item in xmlItems:
    if not isinstance(item, IndexItem):
      xmlItemsComplete.append(item)
    else:
      type=None
      line=item.header.get_text()
      sieheMatch=re.search('siehe (.*)',line)
      if sieheMatch:
        n=sieheMatch.group(1).strip()
        itemTag = soup.new_tag("indexItem")
        for i in xmlItems:
          if not isinstance(i, IndexItem):
            #print(i['value'])
            if n in i['value'].strip():
              type=i['type']
              itemTag['type']=type
              print(type)
              itemTag['value']=item.header.b.get_text()
              itemTag['id']='item_'+str(item.header['tmp_id'])
              #print(itemTag)
              if not type:
                print (value+" konnte nicht aufgeloest werden!?!")
              if type=='location':
                settleType=i.find('location-header').placeName.settlement['type']
                #print('settletype: '+ settleType)
                locHeadTag=soup.new_tag("location-header")
                placeNameTag=soup.new_tag("placeName")
                settleTag=soup.new_tag("settlement")
                itemTag.append(locHeadTag)
                locHeadTag.append(placeNameTag)
                placeNameTag.append(settleTag)
                settleTag['type']=settleType
                placeNameTag.append(item.header.get_text())
                
              if type=='family':
                famHeaderTag=soup.new_tag('family-header')
                famNameTag=soup.new_tag('family-name')
                nameTag=soup.new_tag('name')
                
                itemTag.append(famHeaderTag)
                famHeaderTag.append(famNameTag)
                famNameTag.append(nameTag)
                nameTag.append(item.header.get_text())
                
              xmlItemsComplete.append(itemTag)
              break
        #print (n+' nicht aufgeloest')
      print(type)

  print("Items classified")  
  print("Familien: "+ str(len(families)))
  print ("Unclassified: "+ str(len(unclassified)))
  print("Persons: " + str(len(persons)))
  print("Landmarks: " + str(len(landmarks)))
  print("Personengruppen: " + str(len(persongroups)))
  print("Locations: " + str(len(locations)))
  print("Siehe: " + str(len(siehe)))

  with open ('extractedFamilies.txt', 'w') as file:
    for family in families:
      file.write(str(family))
  with open ('extractedPersons.txt', 'w') as file:
    file.write(str(persons))
  with open ('extractedPersongroups.txt', 'w') as file:
    file.write(str(persongroups))
  with open ('extractedUnclassified.txt', 'w') as file:
    file.write(str(unclassified))
  with open ('extractedLandmarks.txt', 'w') as file:
    file.write(str(landmarks))
  with open ('extractedLocations.txt', 'w') as file:
    for location in locations:
      file.write(str(location))

  with open ('extractedFamilies.txt', 'w') as file:
    file.write(str(families))


  '''with open ('extractedSieheRead4.txt', 'w') as file:
    for item in siehe:
      file.write(item.header.get_text().encode('utf-8') +"\n" + \n")'''
      


  with open ('allXmlItems.xml', 'w') as file:
    for item in xmlItemsComplete:
      file.write(item.encode('utf-8') + "\n")
  print ("allXmlItems.xml ausgegeben")
      
  with open ('prettyXmlItems.xml', 'w') as file:
    for item in xmlItemsComplete:
      file.write(item.prettify().encode('utf-8') + "\n")

  with open ('extractedItems.txt', 'w') as file: #
    file.write(str(items))
    
  writeHeaders()
  writeHeaderTexts()
  print('Itmes extracted')

  with open ('famBodyXML.xml', 'w') as file:
    for family in families:
      x= listingBodyToXML(family.body)
      #print(x)
      file.write(str(x))
      file.write("\n")

  # legt mit forenames.txt eine Datei mit Vornamen an
  with codecs.open ('forenames2.txt', 'w', "utf-8") as file:
    file.write('|'.join(forenames))

  print ('Forenames.txt angelegt. Anzahl der Vornamen: '+str(len(forenames)))




####################### 7. TODO ##############################################

### wenn 2fach eingerueckt
### wenn als letztes
# Bucherbach: Keller (Hans danach weg)
# Familie Ihn
# conc-body ueberpruefen und variablen umbenennen
# Bindestriche sammeln
# Ihn
# Kursivdrucke bahalten als quotes

# Ebersingen, Gemuend
# Franken, Hergesheim, Kigelat/Kuechelar

# <listing-body><members><person><persName><forename>