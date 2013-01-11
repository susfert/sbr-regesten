"""
This module extracts the index xml from the Sbr Regesten.

Author: Susanne Fertmann <s9sufert@stud.uni-saarland.de>
"""


from bs4 import BeautifulSoup, Tag, NavigableString
import codecs
import string
import re
import sys

sys.setrecursionlimit(10000)


soup = BeautifulSoup()
persons = []
persongroups = []
locations = []
landmarks = []
unclassified = []
families = []
siehe = [] # to collect items that will be classified later through their reference with "siehe"

person_id = 0


with codecs.open ('resources/forenames.txt', 'r', "utf-8") as file:
    forenameList=[]
    for forename in file:
        forenameList.append(forename.strip())


with codecs.open("sbr-regesten.xml", "r", "utf-8") as f:
    s = BeautifulSoup(f)
    regSoup = s.regesten
    regestenList=[]
    if regSoup:
        regestenList = regSoup.findAll('regest')


########################## 1. Preprocessing ########################

# deletes all span-tags
def del_span_tags(htmlString):
    ''' Deletes all span tags in a html string. '''
    htmlString = re.sub('\</?span.*?\>', '', htmlString)
    return htmlString
    

def del_empty_tags(htmlString):
  '''
  Deletes (unwraps) empty i-tags.
  '''
  htmlString = re.sub('(?u)(<i[^<>]*?>)([, \-]*)(</i>)', '\g<2>', \
                      htmlString)
  return htmlString


def join_b_tags(htmlString):
    '''
    Joins b-tags in a html string if there is nothing in between or only a comma.
    '''
    htmlString = re.sub('(?u)(</b>)([(:?<.*?>), ]*)(<b>)', '\g<2>', \
                        htmlString)
    return htmlString


def join_i_tags(htmlString):
    '''
    Joins i-tags in a html string if there is nothing in between or only a comma.
    '''
    htmlString = re.sub('(?u)(</i>)([(:?<.*?>), ]*)(<i>)', '\g<2>', \
                        htmlString)
    return htmlString


def exclude_comma(htmlString):
    ''''
    Puts ending commas from inside i-tags outside the i-tag.
    '''
    htmlString = re.sub('(?u)(, ?)(</i>)', '\g<2>\g<1>', htmlString)
    htmlString = re.sub('(?u)(<i[^<>]*>)((:? ?, ?)+)', '\g<2>\g<1>', \
                        htmlString)
    return htmlString  


def preprocess(soup):
    ''' Preprocesses a BeautifulSoup item (html). '''
    htmlString = unicode(soup)
    htmlString = del_span_tags(htmlString)
    htmlString = del_empty_tags(htmlString)
    htmlString = join_b_tags(htmlString)
    htmlString = join_i_tags(htmlString)
    htmlString = exclude_comma(htmlString)
    soup = BeautifulSoup(htmlString)
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



########################  3. ITEMPARSER   ##########################


def get_regest_ID(reg_ref):
    ''' Seaches the restesten part of the xml to match a given reg-ref to its corresponding regest, returning its id.
    As the regesten part of the xml was not available during development, it's probably not fully working (not tested).
    If no regest is found, the default value of regest_0 (the first regest) will be returned.'''
  
    defaultID = 'regest_99999'
    idList = []
    count = False
    countR = 0
    reg_ref=reg_ref.strip(' +')
  
    for regest in regestenList:
        if countR > 10:
            break
        if count:
            countR += 1
        
        if regest.date.get_text().startswith(reg_ref):
            idList.append(regest['id'])
            count = True
            
    if len(idList) == 1:
        return idList[0]
    else:
        #print('keine eindeutige regestzuweisung moeglich:' + str(idList))
        return defaultID 

    
def find_index_refs(text):
    '''
    Finds and tags index-refs in a given string.
    '''
    indexRefsTag = None
    sieheMatch = re.match('(.*?)(m?i?t? [Ss]iehe[^0-9\)\(]*$)', text)
    if sieheMatch:
        text = sieheMatch.group(1)
        siehe = sieheMatch.group(2)
        indexRefsTag = soup.new_tag('index-refs')
        indexRefsTag.append(siehe)
        
    return text, indexRefsTag


def parse_mentionings(soup, t):
    '''
    Finds and tags mentionings in a given soup.
    '''
    mentioningsTag = None
    text = t
    mentionings = []
    ment = '((?:\[?\+\]? )?[01][0-9]{3}\-?\/?[01]?[0-9]?\-?[0-3]?'\
          '[0-9]? ?\([a-f]?k?u?r?z? ??n?a?c?h?v?o?r?n?t?e?u?m?p?o?s?t?a?n?t?e?'\
          '\??\.?\) ?)( Anm\.)?|((?:\[?\+\]? )?[01][0-9]{3}\-?[01]?'\
          '[0-9]?\-?[0-3]?[0-9]?(\/[01][0-9])? ?\(?z?w?i?s?c?h?e?n?\)?)'
    
    mentMatch = re.match('(.*?)('+ment+',? ? ?)$', text)
    while mentMatch:
        text = mentMatch.group(1)
        menti = mentMatch.group(2)
        mentionings.insert(0, menti)
        mentMatch = re.match('(.*?)('+ment+')[,\.]{1,} ? $', text)
    
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
            id = get_regest_ID(reg_ref)
            reg_refTag['regest'] = id
            
            mentioningsTag.append(reg_refTag)
    return (text, mentioningsTag)


def parse_addnames(parentTag, text):
    ''' Parses additional names (which are writtenin italics in parenthesis). '''
    altNMatch = re.match("(?u)(.*?\(\<i.*?\>)(.*?)\)(.*, .*)", text)
    r = None
    if altNMatch:
        altNames = BeautifulSoup(altNMatch.group(2)).get_text().strip()\
                  .split(',')
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


def parse_pers_name (nameTag, personName):
    ''' Parses a person name with the attributes: forename, genName and addNames. '''
    foreTag = soup.new_tag("forename")
    
    genNameKeys = "der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\."\
                  "|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\."\
                  "|Junior|Jr|Senior|Sr|der Junge|der Alte"
    genNameMatch = re.search("(.*?)(\[?" + genNameKeys + "\]?)(.*)", \
                            personName)
    addNameMatch = re.search("(.*?)" + "(gen\.|den man nennet|"\
                             "dem man sprichet)" + "(.+)", personName)
    
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


def equal_matchgroup(match,i,label):
    try:
        return match.group(label) == match.group(i)
    except IndexError:
        return False
    
def get_match_label(match,i):
        matchDict = match.groupdict()
        for groupName in matchDict.keys():
            if equal_matchgroup(match,i,groupName):
                return groupName
        return None
        
def annotate_groupnames(m, nameTag):
    for i in range(1,len(m.groups())+1):
        label = get_match_label(m,i)
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

def parse_place_name (placeNameTag, text, ref_point=True):
       
    districtKeys = "Gem|Stadtverband [^;,]+|Gde\. [^,;]+|[\w-]+-Kreis|"\
                   "Kr\. [^,;]+|[-\w]+kreis|Stadt [\w][\w]\.|Stadt [\w-]+|"\
                   "Kreis [^;,]+"
    district = "(?:"+districtKeys + ")(?:, (?:" + districtKeys + "))?"
    regionKeys = "Dep\.,? [A-Za-z-]+|SL|NRW|By|RLP|BW|Prov\..+|Hessen"
    country = "B|F|NL|CH|Lux|It|L|Spanien|T.rkei"
    countryKeys = "(?:"+country+")(?![\w])"
    
    if ref_point:
        refPointMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)'\
                              '(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|'\
                              '[^\w]+W.stung.*?[^\w]+)(?=(?:' + district + \
                              '|' + regionKeys + '|' + countryKeys+'))', text) 
        if refPointMatch:
            placeNameTag, index = annotate_groupnames(refPointMatch, placeNameTag)
            text=text[index:]
    else:
        m = re.match('(.*?)(?=(?:'+district+'|'+regionKeys+'|'+countryKeys+'))'
                     '(.*)', text)
        if m:
            placeNameTag.append(m.group(1))
            text=m.group(2)
    
    
    distRegMatch = re.match('(?u)(?P<district>'+ district + ')(.*)'\
                            '(?P<region>' + regionKeys + ')(.*)', text)
    distRegCountMatch = re.match('(?u)(?P<district>'+ district +')(.*)'\
                                '(?P<region>'+ regionKeys + ')(.*)'\
                                '(?P<country>' + countryKeys + ')(.*)', text)
    distCountMatch = re.match('(?u)(?P<district>'+ district +')(.*)'\
                              '(?P<country>' + countryKeys + ')(.*)', text)
    regCountMatch = re.match('(?u)(?P<region>'+ regionKeys + ')(.*)'\
                             '(?P<country>' + countryKeys + ')(.*)', text)
    countMatch = re.match('(?u)(?P<country>'+ countryKeys + ')(.*)', text)
    regMatch = re.match('(?u)(?P<region>'+ regionKeys + ')(.*)', text)
    distMatch = re.match('(?u)(?P<district>'+ district + ')(.*)', text)
    settleMatch = re.match('(?u)([^\w]?(?:siehe [\w/-]+)?)'\
                           '(?P<reference_point>[\w\.\/ -]*?)(.*)', text)
    
    possibleMatches = [distRegCountMatch, distRegMatch, distCountMatch, \
                      regCountMatch, regMatch, distMatch, countMatch, \
                      settleMatch]
    for m in possibleMatches:
        if m:
            placeNameTag, index = annotate_groupnames(m, placeNameTag)
            
            if "region" in m.groupdict():     
                region = m.group("region")
                if "Prov" in region:
                    placeNameTag.find("region")['type'] = 'Provinz'
                elif "Dep" in region:
                    placeNameTag.find("region")['type'] = 'Departement'
                elif "NRW" or "SL" or "RLP" or "By" or "BW" or "Hessen"\
                        in region:
                    placeNameTag.find("region")['type'] = 'Bundesland'
                    
            break

    return (placeNameTag)


def loc_header_to_XML(header):
    '''
    Converts an html header into a xml location header.
    '''
    headerTag = soup.new_tag("location-header")
    placeNameTag = soup.new_tag('placeName')
    
    settleTag = soup.new_tag("settlement")
    placeNameTag.append(settleTag)
 
    # Wuestungen
    wuestMatch = re.search('(Staerk, W.stungen Nr. [0-9][0-9]?)', \
                           header.get_text())
    w = False
    if wuestMatch:
        w = True            
        w_ref = wuestMatch.group(0)
        settleTag["w-ref"] = w_ref
    settleTag["w"] = str(w).lower()
 
    # Settlement name 
    name = ''
    rest = ''
    if header.b:               # for location-headers
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
    
    placeNameTag, ohneAddN = parse_addnames(placeNameTag, rest)
    if ohneAddN:
        text = BeautifulSoup(ohneAddN).get_text()
    else:
        text = BeautifulSoup(rest).get_text()

    text, indexRefsTag = find_index_refs(text)
    text, ment = parse_mentionings(soup, text)
    
    # SettlementType, RefPoint, District, Region, Country
    settlement = "Dorf|Stadt|Stadtteil|Burgsiedlung|Burg|ehem. Burg|Hofgut|Hof"\
                 "|Ort|.rtlichkeit|Gemeinde|Kloster|Abtei|Schloss|Herrschaft"\
                 "|Gft\.|Kgr\.|Land|Kgr\.|Herzogtum|Hzgt\.|Grafschaft"\
                 "|F.rstentum|Deutschordenskommende|Bistum|Vogtei"\
                 "|Regierungssitz|Hochstift|Pfarrei|Erzstift|Erzbistum|Dekanat"\
                 "|Domstift|Reichsland|Deutschordensballei|\w*abtei|Wasserburg"\
                 "|M.hle|Zisterzienserabtei|Region"
    settlementKeys = "(?:"+settlement+")(?![\w])"
    settleMatch = re.match('(?u)(.*?)('+ settlementKeys +')(.*?)', text)
    
    if settleMatch:
        placeNameTag, index = annotate_groupnames(settleMatch, placeNameTag)
        text = text[index:]
        settleTag["type"] = settleMatch.group(2)
    else:
        settleTag["type"] = 'unknown'
    
    placeNameTag = parse_place_name(placeNameTag, text)
    
    headerTag.append(placeNameTag)
    
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)
    
    return name.rstrip(', '), headerTag


####################### 3.1.2 Family Header #################################

def fam_header_to_XML(header):
    '''
    Converts an html header into a xml family header.
    '''
    headerTag = soup.new_tag("family-header")

    # Name
    name = header.b.get_text()
    famNameTag = soup.new_tag('family-name')
    nameTag = soup.new_tag('name')
    famNameTag.append(nameTag)
    nameTag.append(name)
    
    ohneB = BeautifulSoup(str(header))
    ohneB.b.decompose()
    

    # Alternative names & locations
    # both appear in parentesis, alternative names in italics, locations not)
    famNameTag, ohneAddN = parse_addnames(famNameTag, unicode(ohneB))
    headerTag.append(famNameTag)
    
    if ohneAddN:
        rest = BeautifulSoup(ohneAddN).get_text()
    else:
        rest = ohneB.get_text()

    parMatch = re.match(r"([^\w]*?)\((.*[A-Za-z][a-z]{1,3}.*)(\), .*)", rest)
    if parMatch:
        headerTag.append(BeautifulSoup(parMatch.group(1)).get_text())
        loc=parMatch.group(2)
        placeNameTag = soup.new_tag('location')
        placeNameTag= parse_place_name(placeNameTag, loc, ref_point=False)
        headerTag.append('(')
        headerTag.append(placeNameTag)
        t = parMatch.group(3)
    else:
        t = BeautifulSoup(rest).get_text()
    
 
    t, indexRefsTag = find_index_refs(t)
    rest, ment = parse_mentionings(soup, t)
    
    headerTag.append(rest)
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)

    return name.rstrip(', '), headerTag



#################### 3.1.3 Landmark Header ##################################

def land_header_to_XML(header):
    '''
    Converts an html header into a xml landmark header.
    '''
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
    

    geogTag, ohneAddN = parse_addnames(geogTag, unicode(ohneB))
    if ohneAddN:
        t = BeautifulSoup(ohneAddN).get_text()
    else:
        t = ohneB.get_text()

    headerTag.append(geogTag)

    text, indexRefsTag = find_index_refs(t)
    t, ment = parse_mentionings(soup, t)

    
    landkey = 'Fluss|Berg|gau[ ,]|Gau|Bach|Talschaft|Tal|Landschaft|Au'\
              '|Waldung|Wald|Gemeindewald'
    landMatch = re.match('(.*)('+landkey+')(.*)', t)
    
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
        
    return name.rstrip(', '), headerTag



#################### 3.1.4 Persongroup Header ###############################

def persgr_header_to_XML(header):
    '''
    Converts an html header into a xml persongroup header.
    '''
    headerTag = soup.new_tag("persongroup-header")
    
    text, indexRefsTag = find_index_refs(header.get_text())
    # name + mentionings
    rest, ment = parse_mentionings(soup, text)
    value = header.b.get_text()
    name = rest
    grNameTag = soup.new_tag("group-name")
    headerTag.append(grNameTag)
    grNameTag.append(name)
    
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)

    return value.rstrip(', '), headerTag



#################### 3.1.5 Person Header ####################################
    
def pers_header_to_XML(header):
    '''
    Converts an html header into a xml person header.
    '''
    headerTag = soup.new_tag("person-header")
    persTag = soup.new_tag("person")
    headerTag.append(persTag)
    global person_id
    persTag['id'] = 'person_'+str(person_id)
    person_id += 1

    # Name
    name = header.b.get_text()
    nameTag = soup.new_tag("persName")
    
    ohneB = BeautifulSoup(str(header))
    ohneB.b.decompose()
    
    text, indexRefsTag = find_index_refs(header.get_text())
    text, ment = parse_mentionings(soup, text)
    description, ment2 = parse_mentionings(soup, ohneB.get_text())

    genNameKeys = "der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite|I\."\
                  "|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.|X\."\
                  "|Junior|Jr|Senior|Sr|der Junge|der Alte|d\.J\."
    roleKeys = "K.nig|Kaiser|Herzog|Graf|Hzg\.|Kg\.|Ks\.|Herzogin|Gf\."\
               "|dt\. Kg\. und r.m\. Ks\.|Gr.fin"
    
    matched = False
    forenameKeys = '|'.join(forenameList)
    
    # Fust von Diebach gen. Knebel
    surForeMatch = re.match('(?u)(?P<surname>[^, ]+?)(, )(?P<forename>' +\
                            forenameKeys + ')([ von]*,? )' , text)
    foreMatch = re.match('(?u)(?P<forename>' + forenameKeys + ')(,)' , text)
    foreSurMatch = re.match('(?u)(?P<forename>' + forenameKeys + ')( )'\
                            '(?P<surname>[^,]+)(,)', text)
    foreVonSurMatch = re.match('(?u)(?P<forename>[\w]+)( )'\
                               '(?P<surname>von [^,]+)(,)', text)
    foreGenRoleMatch = re.match('(?u)(?P<forename>[\w]+)( )(?P<genName>' + \
                                genNameKeys + ')(,? ?)(?P<roleName>' + \
                                roleKeys + '?)', text)
    foreGenMatch = re.match('(?u)(?P<forename>[\w]+)( )(?P<genName>' + \
                            genNameKeys + ')', text)
    foreRoleMatch = re.match('(?u)(?P<forename>' + forenameKeys+')(, )'\
                             '(?P<roleName>' + roleKeys+')', text)
    
    for m in [foreGenRoleMatch, foreGenMatch, surForeMatch, foreVonSurMatch,\
              foreRoleMatch, foreSurMatch, foreMatch]:
        if m and not matched:
            nameTag, index = annotate_groupnames(m, nameTag)
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
        
    return name.rstrip(', '), headerTag


############################## 3.2 Bodies ###########################

def parse_quotes (htmlitem):
    '''
    Parses quotes in a html item. Converts all i-tags into quote-tags.
    Deletes all other tags.
    '''
    quoteMatch_with_comma = re.match('(?u)(.*?)<i.*?>(.{5,}?),(.{5,}?)</i>'\
                                     '(.*)', htmlitem)
    quoteMatch = re.match('(?u)(.*?)(<i.*?>.{5,}?</i>)(.*)', htmlitem)
    
    if quoteMatch_with_comma:
        before_q = BeautifulSoup(quoteMatch_with_comma.group(1)).get_text()
        quote1 = BeautifulSoup(quoteMatch_with_comma.group(2)).get_text()
        quote2 = BeautifulSoup(quoteMatch_with_comma.group(3)).get_text()
        
        if quote1.strip() != '' and quote2.strip() != '':
          parsedItem = before_q + '<quote>' + quote1 + '</quote>,'\
                       + '<quote>' + quote2 + '</quote>'\
                       + parse_quotes(quoteMatch_with_comma.group(4))
                     
        else:
            return unicode(BeautifulSoup(htmlitem).get_text())
        return unicode(parsedItem)    
    
    elif quoteMatch:
        quote = BeautifulSoup(quoteMatch.group(2)).get_text()
        if not 'siehe' in quote and not "Siehe" in quote\
                and quote.strip() != '':
            parsedItem = BeautifulSoup(quoteMatch.group(1)).get_text()\
                         + '<quote>' + quote + '</quote>'\
                         + parse_quotes(quoteMatch.group(3))
            return unicode(parsedItem)
        else:
            return unicode(BeautifulSoup(htmlitem).get_text())
    else:
        return unicode(BeautifulSoup(htmlitem).get_text())



def build_conc_tag(text):
    '''Builds a concept out of a given text.'''
    soup=BeautifulSoup()
    concTag = soup.new_tag('concept')
    rest, ment = parse_mentionings(soup, text)
    nameMatch = re.match('(?P<name>.*?)(?P<description>,{1}.*)',rest)
    if nameMatch:
        concTag, index = annotate_groupnames(nameMatch, concTag)
    else:
        nameTag = soup.new_tag('name')
        nameTag.append(rest)
        concTag.append(nameTag)
    if ment:
        concTag.append(ment)
    return (concTag)



def relConcToXML(liste, prefix):
    '''
    Parses a list of concepts.
    Prefix is given and stored for indentation.
    '''
    relConcTag = soup.new_tag('related-concepts')    
    concList = []
    concTag = None
    for concHTML in liste:
        conc=parse_quotes(concHTML)
        einrueckMatch = re.match('( *?\-)(.*)', conc)
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

        concTag = build_conc_tag(conc)
        relConcTag.append(prefix)
        relConcTag.append(concTag)

    if concList:
            innerRelConcTag = relConcToXML(concList, prefix + ' -')
            if concTag:
                concTag.append(innerRelConcTag)
            else:
                concTag = innerRelConcTag
            if relConcTag:
                relConcTag.append(concTag)
    
    return relConcTag





################# 3.2.1 ListingBody (FamilyBody, PersongroupBody) ###########


def listing_body_to_XML(body):
    '''
    Converts an html body into a xml body type listing-body.
    Listing bodies have persons on the first level of indentation.
    The rest of levels are parsed as concepts.
    '''
    listBodyTag = soup.new_tag("listing-body")
    membersTag = soup.new_tag("members")
    listBodyTag.append(membersTag)

    personList = str(body).split("<br>")
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
    
        rest, ment = parse_mentionings(soup, person.get_text())
        personAttrList = rest.split(",")
        personName=personAttrList[0]
        personTag = soup.new_tag('person')
        global person_id
        personTag['id'] = 'person_'+str(person_id)
        person_id += 1
        membersTag.append(personTag)
        nameTag = soup.new_tag("persName")
        personTag.append(nameTag)
        parse_pers_name(nameTag, personName)

        
        if personName:
            possForename = BeautifulSoup(personName.split()[0]).get_text().\
                           strip(' ()[].,;')
            if possForename != 'Leibeigene' and possForename != 'Herrin' and\
                  possForename != "Rechtshandlung" and possForename != "Frau"\
                  and possForename != "Edelmann":
                if not possForename in forenameList:
                    forenameList.append(possForename)
    

        attrs = ""
        if len(personAttrList)>1:
            possAddName = personAttrList[1]
            if re.match("[ ]"+"(gen\.|den man nennet|dem man sprichet)"
                        +"(.+)", possAddName):
                nameTag.append(", ")
                parse_pers_name(nameTag, possAddName)
                personAttrList = personAttrList[1:]
        
        for attr in personAttrList[1:]:
            attrs = attrs + "," + attr

        persInfoTag = soup.new_tag('description')
        if attrs:
            personTag.append(persInfoTag)
            persInfoTag.append(attrs)
        
        if ment:
            personTag.append(ment)
        
    return listBodyTag


############## 3.2.2 RelatedConceptsBody (Location, Landmark, Person) #######

def relconc_body_to_XML(body):
    '''
    Converts an html body into a xml body type concept-body.
    '''
    listBodyTag = soup.new_tag("concept-body")
    bodyList = str(body).split("<br>")

    if not body.get_text():
        return listBodyTag
    
    relTag = soup.new_tag("related-concepts")
    listBodyTag.append(relTag)
    concList = []
    conceptTag = None
    for conceptHTML in bodyList:
        concept=parse_quotes(conceptHTML)
        
        einrueckMatch = re.match('( *-)(.*)', concept)
        if einrueckMatch:
            if einrueckMatch.group(2).strip().startswith('-')\
                    and not concList:
                print einrueckMatch.group(2)
                raise ExtractorException('Ill-formed HTML (body): '\
                      'unexpected indentation level in inner related concept')
            concList.append(einrueckMatch.group(2))
            continue
            
        elif concList:
            relConcTag = relConcToXML(concList, ' -')
            conceptTag.append(relConcTag)
            concList = []
    
    
        conceptTag=build_conc_tag(concept)
        relTag.append(conceptTag)
 
    if concList:
            relConcTag = relConcToXML(concList, ' -')
            if conceptTag:
                conceptTag.append(relConcTag)
            else:
                raise ExtractorException('Ill-formed HTML (body): '\
                      'unexpected indentation level in related concept')

    return listBodyTag


############################ 4. Parser ##################################

############################ 4.1 Familiy Parser    #####################

def fam_to_XML(family, id):
    itemTag = soup.new_tag("item")
    value, itemHeader = fam_header_to_XML(family.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'family'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = listing_body_to_XML(family.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag


################## 4.2 PersongroupParser #############

def persgr_to_XML(persongroup, id):
    ''' Converts an html item into a completely annotated xml persongroup item. '''
    itemTag = soup.new_tag("item")
    value, itemHeader = persgr_header_to_XML(persongroup.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'persongroup'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = listing_body_to_XML(persongroup.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    
    
################## 4.3 PersonParser #############

def pers_to_XML(person, id):
    ''' Converts an html item into a completely annotated xml person item. '''
    itemTag = soup.new_tag("item")
    value, itemHeader = pers_header_to_XML(person.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'person'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = relconc_body_to_XML(person.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    
    
################## 4.4 LocationParser #############

def locToXML(location, id):
    ''' Converts an html item into a completely annotated xml location item. '''
    itemTag = soup.new_tag("item")
    value, itemHeader = loc_header_to_XML(location.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'location'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = relconc_body_to_XML(location.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    
    
################## 4.5 LandmarkParser #############

def landToXML(landmark, id):
    ''' Converts an html item into a completely annotated xml landmark item. '''
    itemTag = soup.new_tag("item")
    value, itemHeader = land_header_to_XML(landmark.header)
    itemTag.append(itemHeader)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'landmark'
    itemTag['value'] = value
    itemBody = relconc_body_to_XML(landmark.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    


########################## 5. index_to_xml    ################################

def build_header_body(h, b, lineList):
    if len(lineList) > 0:
        firstLineText=BeautifulSoup(lineList[0]).get_text().strip()
        
        if firstLineText.startswith(('siehe', 'mit siehe', 'vgl.')):
            h += lineList[0]
            lineList = lineList[1:]
            h, b = build_header_body(h, b, lineList)
         
        else:
            b = '<br>'.join(lineList)
    return (h, b)



def index_to_xml():
    '''
    Main function. Finds the index in html/sbr-regesten.html, converts
    it into xml and writes it into index.xml.
    '''
    print('Index Extractor is working ..')
    text = ""
    t = ""

    with codecs.open("html/sbr-regesten.html", "r", "cp1252") as f:
        text = f.read()
        text = unicode(text)
        t2 = text.replace("\n"," ")
        t = t2.replace("\r","")

    soup = BeautifulSoup(t)

    indexTag = soup.new_tag('index')
    indexInfoTag = soup.new_tag('index-info')
    indexTag.append('Index \n')
    indexTag.append(indexInfoTag)

    items = []

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
                htmlItem=preprocess(htmlItem)
                s = unicode(htmlItem)

                lineList = s.split('<br>')
                h = lineList[0]
                b = ''
                restList = lineList[1:]
                
                h,b = build_header_body(h,b,restList)

                h = '<itemHeader>'+h+'</itemHeader>'
                b = '<itemBody>'+b+'</itemBody>'
                header = BeautifulSoup(h)
                body = BeautifulSoup(b)
                item = IndexItem(header, body)
                items.append(item)

    xmlItems = []
    id = -1

    for item in items:
        header = item.header.get_text()
        
        famMatch = re.search('[Ff]amilie|Adelsgeschlecht', header)
        
        locMatch = re.search('[Ss]tadt,|Stadtteil|Dorf|Burg |Hof |Hofgut|'\
                             'Gemeinde |Ort |.rtlichkeit |Kloster|Abtei|'\
                             'Schloss|Herrschaft|Gft\.|Kgr\.|Region|Gebiet|'\
                             'Land |Kgr\.|Herzogtum|Hzgt\.|[Gg]rafschaft|'\
                             'F.rstentum|Deutschordenskommende|RLP|Gde\.|'\
                             'Bistum|Vogtei|Regierungssitz|Hochstift|'\
                             'Pfarrei|W.stung|F\)|Erzstift|, Erzbistum|'\
                             'Dekanat|Domstift|Reichsland|Deutschordensballei'\
                             '|M.hle|Wallfahrt|Land |Reise|lothr. Amt|'\
                             'Deutschordenshaus|[Ss]tadt (?!S)', header)
        
        grpMatch = re.search('Notare|, Grafen|, Markgrafen|[Hh]erz.ge|'\
                             '[Bb]isch.fe|Edelknechte|Herrn von|[Ff].rsten|'\
                             'Personen|K.nige|Ritter von|Einwohner|P.pste|'\
                             'Wildgrafen|Herren|(?<!, )Dominikaner', header)
        
        persMatch = re.search('Bischof|Pastor|Graf |Papst |II\.|I\.|III\.|'\
                              'IV\.|V\.|Hzg\.|Bf\.|Adliger|Herr |Frau |Kg\.|'\
                              'Elekt|meister|Ritter|, Schulthei.|, Herzogin|'\
                              'Amtmann|Lehensmann|Vetter von|Markgraf |'\
                              'Pfalzgraf|Ebf\.|, Herzog|, Dominikaner|Hans|'\
                              'Erzpriester|[dD]iakon|Provinzial|r.m\. K.nig|'\
                              'Kammermajor|Witwe|Junker|Stephan|Jacob|Klaus|'\
                              'Elisabeth|Fabricio|Nikolaus|Alheim|Gerbod', \
                              header)
        
        landMatch = re.search('Fluss|Berg|gau[ ,]|Gau|Bach|Tal|Landschaft|'\
                              'Wald|Waldung|Gemeindewald|Au|furt|Engenberg', \
                              header)
        
        sieheMatch = re.search('siehe', header)
        
        if famMatch:
            x = fam_to_XML(item, id)
            xmlItems.append(x)
            families.append(item)

        elif locMatch:
            pass
            x = locToXML(item, id)
            xmlItems.append(x)
            locations.append(item)

        elif grpMatch:
            x = persgr_to_XML(item, id)
            xmlItems.append(x)    
            persongroups.append(item)

        elif persMatch:
            x = pers_to_XML(item, id)
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
                              print (value+": unknown type.")
                                
                            if type == 'location':
                              settleType = i.find('location-header').placeName\
                                            .settlement['type']
                              value, header = loc_header_to_XML(item.header)
                              header.placeName.settlement['type'] = settleType
                              itemTag.append(header)
                                
                            if type == 'family':
                              value, header = fam_header_to_XML(item.header)
                              itemTag.append(header)

                            xmlItemsComplete.append(itemTag)
                            break


    # adds forenames to forenames.txt if found new forenames
    with codecs.open ('resources/forenames.txt', 'w', "utf-8") as file:
        file.write('\n'.join(forenameList))
        
    with open ('index40.xml', 'w') as file:
        for item in xmlItemsComplete:
            indexTag.append(item)
            indexTag.append('\n')
        file.write(indexTag.encode('utf-8'))
    print ("Created index.xml")
    print('Index converted into xml.')