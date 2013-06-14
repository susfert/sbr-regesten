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
siehe = []

person_id = 0


with codecs.open ('resources/forenames.txt', 'r', 'utf-8') as file:
    forenameList=[]
    for forename in file:
        forenameList.append(forename.strip())



########################## 1. Preprocessing ########################

def del_span_tags(htmlString):
    '''
    Delete all span-tags in an HTML string. 
    <span style='color:windowtext'>Tentelingen</span> --> Tentelingen
    '''
    htmlString = re.sub('\</?span.*?\>', '', htmlString)
    return htmlString
    

def del_empty_tags(htmlString):
  '''
  Unwrap i-tags containing only whitespaces, commas or hyphen in an
  html string.
  <i style='mso-bidi-font-style:normal'>-</i>' --> -
  '''
  htmlString = re.sub('(?u)(<i[^<>]*?>)([, \-]*)(</i>)', '\g<2>', htmlString)
  return htmlString


def join_b_tags(htmlString):
    '''
    Join all pairs of b-tags in an HTML string if there is only a
    comma or nothing in between.
    <b>...</b>, <b>...</b> --> <b>..., ...</b>
    '''
    htmlString = re.sub('(?u)(</b>)([(:?<.*?>), ]*)(<b>)', '\g<2>', \
                        htmlString)
    return htmlString


def join_i_tags(htmlString):
    '''
    Join all pairs of i-tags in an HTML string if there is only a
    comma or nothing in between.
    <i>...</i>, <i>...</i> --> <i>..., ...</i>
    '''
    htmlString = re.sub('(?u)(</i>)([(:?<.*?>), ]*)(<i>)', '\g<2>', \
                        htmlString)
    return htmlString


def exclude_comma(htmlString):
    ''''
    Move commas at the end of i-tags outside.
    <i>Cristyne,</i> --> <i>Cristyne</i>,
    '''
    htmlString = re.sub('(?u)(, ?)(</i>)', '\g<2>\g<1>', htmlString)
    htmlString = re.sub('(?u)(<i[^<>]*>)((:? ?, ?)+)', '\g<2>\g<1>', \
                        htmlString)
    return htmlString  


def preprocess(soup):
    ''' Regularize a BeautifulSoup HTML item.  '''
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
    '''Raised when HTML input is irregular or unexpected.'''
    def __init__(self, text):
        self.text = text
    def __str__(self):
        return self.text

class IndexItem:
    '''Wrapper for an HTML sequence corresponding to an index item.'''
    def __init__(self, header, body):
        self.header = header
        self.body = body
    def __repr__(self):
        return (str(self.header)+'\n'+str(self.body))+'\n'+'\n'



########################  3. ITEMPARSER   ##########################


def get_regest_ID(reg_ref):
    '''
    TO BE IMPLEMENTED
    Return default value regest_99999
    (Search the restesten to match a given reg-ref to its
    corresponding regest, return the regest's id.)
    '''
    defaultID = 'regest_99999'
    return defaultID 

    
def find_index_refs(text):
    '''
    Find references to other index entries at the end of a given 
    string. Tag them as index-refs. Do not solve the references.
    Return the string without references and the BeautifulSoup-tag
    index-refs.
    '''
    indexRefsTag = None
    sieheMatch = re.match('(.*?)(m?i?t? [Ss]iehe[^0-9\)\(]*$)', text)
    if sieheMatch:
        text = sieheMatch.group(1)
        siehe = sieheMatch.group(2)
        indexRefsTag = soup.new_tag('index-refs')
        indexRefsTag.append(siehe)
    return text, indexRefsTag


def parse_mentionings(text):
    '''
    Find, solve and tag references to regests (mentionings) in a given
    string. Return the string without references and the
    BeautifulSoup-tag mentioned-in.
    '''
    soup = BeautifulSoup()
    mentioningsTag = None
    mentionings = []
    
    affix = ' \([a-f]?k?u?r?z? ?n?a?c?h?v?o?r?n?t?e?u?m?p?o?s?t?a?n?t?e?z?w?i?s?c?h?e?c?a?\.?n?n?o?c?h? ?V?a?t?e?r?\??\.?\)'
    
    sing_ment = '(?:\[?\+\]? )?[01][0-9]{3}\-?\/?[01]?[0-9]?\-?[0-3]?[0-9]?(\/[01][0-9])?('\
          + affix +')*( Anm\.)?'
    
    ment = sing_ment + '( ?[-/] ?' + sing_ment + ')?'
    
    # 1525 (a) (ca.)
    # 1544-12-25 (nach) (a)
    
    mentMatch = re.match('(.*?)('+ment+'),? ? ?$', text)
    
    while mentMatch:
        text = mentMatch.group(1)
        menti = mentMatch.group(2)
        mentionings.insert(0, menti)
        mentMatch = re.match('(.*?)('+ment+')[,\.]{1,} ? $', text)
    
    if mentionings:
        mentioningsTag = soup.new_tag('mentioned-in')
        notFirstEl = False
        for reg_ref in mentionings:
            if notFirstEl:
                mentioningsTag.append(', ')
            else:
                notFirstEl = True
            reg_refTag = soup.new_tag('reg-ref')
            reg_refTag.append(reg_ref)
            id = get_regest_ID(reg_ref)
            reg_refTag['regest'] = id
            mentioningsTag.append(reg_refTag)
    return (text, mentioningsTag)


def parse_addnames(parentTag, text):
    '''
    Parse additional names (= strings written in italics in 
    parenthesis) and add them to a given parent tag.
    '''
    altNMatch = re.match('(?u)(.*?\(\<i.*?\>)(.*?)\)(.*, .*)', text)
    r = None
    if altNMatch:
        altNames = BeautifulSoup(altNMatch.group(2)).get_text().strip()\
                  .split(',')
        addNamesTag = soup.new_tag('addNames')
        addNamesTag.append(BeautifulSoup(altNMatch.group(1)).get_text())

        parentTag.append(addNamesTag)
        notFirstEl = False
        for altName in altNames:
            if notFirstEl:
                 addNamesTag.append(',')
            else:
                notFirstEl = True
            addNameTag = soup.new_tag('addName')
            addNameTag.append(altName)
            addNamesTag.append(addNameTag)
        addNamesTag.append('')
        addNamesTag.append(')')
        r = altNMatch.group(3)
    return (parentTag, r)


def parse_pers_name (nameTag, personName):
    '''
    Parse a person name (string) extracting surname, forename, addNames
    (additional names) and genName (generational name, e.g. senior,
    II., the first). Add them to a given name tag. Use hardcoded lists
    for generational names and for additional name triggers.
    '''
    foreTag = soup.new_tag('forename')
    
    genNameKeys = 'der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite'\
                  '|I\.|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.'\
                  'XI\.|X\.|Junior|Jr|Senior|Sr|der Junge|der Alte'
    genNameMatch = re.search('(.{3,}?)( \[?)(' + genNameKeys + '\]?)(.*)', \
                            personName)
    addNameMatch = re.search('(.*?)' + '(gen\.|den man nennet|'\
                             'dem man sprichet)' + '(.+)', personName)
    
    if genNameMatch:
        foreName = genNameMatch.group(1)
        if foreName.strip() != '':
            nameTag.append(foreTag)     
            foreTag.append(foreName) 
        nameTag.append(genNameMatch.group(2))
        genName = genNameMatch.group(3)
        restName = genNameMatch.group(4)
        genNameTag = soup.new_tag('genName')
        nameTag.append(genNameTag)
        genNameTag.append(genName)     
        nameTag.append(restName)
        
    elif addNameMatch:
        foreName = addNameMatch.group(1)
        gen = addNameMatch.group(2)
        addName = addNameMatch.group(3)
        if foreName.strip() != '':
            nameTag.append(foreTag)     
            foreTag.append(foreName) 
        addNamesTag = soup.new_tag('addNames')
        addNameTag = soup.new_tag('addName')
        nameTag.append(gen)
        nameTag.append(addNamesTag)
        addNamesTag.append(addNameTag)
        addNameTag.append(addName)
        
    else:
        nameTag.append(foreTag)     
        foreTag.append(personName)


def equal_matchgroup(match,i,label):
    '''Check if the match group at position i has a certain label.'''
    try:
        return match.group(label) == match.group(i)
    except IndexError:
        return False


def get_match_label(match,i):
    '''Return the label of the i-th match group.'''
    matchDict = match.groupdict()
    for groupName in matchDict.keys():
        if equal_matchgroup(match,i,groupName):
            return groupName
    return None


def annotate_groupnames(m, nameTag):
    '''
    Tag the content of each match group with its group name. Append all
    tags to a given nameTag. Return nameTag and the index after the
    last match.
    '''
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

def del_b_tag(header):
    '''Delete b-tags with their contents in a BeautifulSoup-item.'''
    hasNoB = BeautifulSoup(str(header))
    hasNoB.b.decompose()
    return hasNoB

####################### 3.1. Header Parser ####################################

####################### 3.1.1 LocationHeader ##################################

def parse_place_name (placeNameTag, text, ref_point=True):
    '''
    Parse a place name. Extract and tag reference-points, districts,
    regions, coutries. A reference point is everything before the first
    district/region/coutry respectively, if it is not information about
    an abandoned village (Wuestung). Use hardcoded lists of
    keys/triggers for districts, regions and countries. Use the first
    matching regex for tagging.
    '''   
    districtKeys = 'Gem|Stadtverband [^;,]+|Gde\. [^,;]+|[\w-]+-Kreis|'\
                   'Kr\. [^,;]+|[-\w]+kreis|Stadt [\w][\w]\.|Stadt [\w-]+|'\
                   'Kreis [^;,]+'
    regionKeys = 'Dep\.,? [A-Za-z-]+|SL|NRW|By|RLP|BW|Prov\..+|Hessen'
    countryKeys = 'B|F|NL|CH|Lux|It|L|Spanien|T.rkei|Estland'
    
    district = '(?:' + districtKeys + ')(?:, (?:' + districtKeys + '))?'
    region = regionKeys
    country = '(?:' + countryKeys + ')(?![\w])'
    
    if ref_point:
        refPointMatch = re.match('(?u)([^\w]*? ?(?:siehe [\w/-]+)?)'\
                              '(?P<reference_point>[\w\.\/ -]*?)([^\w-]+|'\
                              '[^\w]+W.stung.*?[^\w]+)(?=(?:' + district + \
                              '|' + region + '|' + country+'))', text) 
        if refPointMatch:
            placeNameTag, index = annotate_groupnames(refPointMatch,\
                                                      placeNameTag)
            text=text[index:]
    else:
        m = re.match('(.*?)(?=(?:' + district + '|' + region + '|' + \
                    country + '))(.*)', text)
        if m:
            placeNameTag.append(m.group(1))
            text=m.group(2)
    
    distRegMatch = re.match('(?u)(?P<district>'+ district + ')(.*)'\
                            '(?P<region>' + region + ')(.*)', text)
    distRegCountMatch = re.match('(?u)(?P<district>'+ district +')(.*)'\
                            '(?P<region>'+ region + ')(.*)'\
                            '(?P<country>' + country + ')(.*)', text)
    distCountMatch = re.match('(?u)(?P<district>'+ district +')(.*)'\
                            '(?P<country>' + country + ')(.*)', text)
    regCountMatch = re.match('(?u)(?P<region>'+ region + ')(.*)'\
                            '(?P<country>' + country + ')(.*)', text)
    countMatch = re.match('(?u)(?P<country>'+ country + ')(.*)', text)
    regMatch = re.match('(?u)(?P<region>'+ region + ')(.*)', text)
    distMatch = re.match('(?u)(?P<district>'+ district + ')(.*)', text)
    settleMatch = re.match('(?u)([^\w]?(?:siehe [\w/-]+)?)'\
                            '(?P<reference_point>[\w\.\/ -]*?)(.*)', text)
    
    possibleMatches = [distRegCountMatch, distRegMatch, distCountMatch, \
                      regCountMatch, regMatch, distMatch, countMatch, \
                      settleMatch]
    for m in possibleMatches:
        if m:
            placeNameTag, index = annotate_groupnames(m, placeNameTag)
            
            if 'region' in m.groupdict():     
                region = m.group('region')
                if 'Prov' in region:
                    placeNameTag.find('region')['type'] = 'Provinz'
                elif 'Dep' in region:
                    placeNameTag.find('region')['type'] = 'Departement'
                elif 'NRW' or 'SL' or 'RLP' or 'By' or 'BW' or 'Hessen'\
                        in region:
                    placeNameTag.find('region')['type'] = 'Bundesland'
            break

    return (placeNameTag)


def loc_header_to_XML(header):
    '''
    Convert a preprocessed HTML index-item header into an XML location
    header.
    '''
    headerTag = soup.new_tag('location-header')
    placeNameTag = soup.new_tag('placeName')
    
    settleTag = soup.new_tag('settlement')
    placeNameTag.append(settleTag)
 
    # Abandoned villages
    avMatch = re.search('(Staerk, W.stungen Nr. [0-9]{1,2})', \
                           header.get_text())
    w = False
    if re.search('W.stung', header.get_text()):
        w = True
    if avMatch:
         settleTag['av-ref'] = avMatch.group(0)
    settleTag['abandoned-village'] = str(w).lower()
 
    # Settlement name + additional names
    if header.b:
        name = header.b.get_text()
        hasNoB = del_b_tag(header)
        rest = unicode(hasNoB)
    
    settleTag.append(name)
    
    placeNameTag, hasNoAddN = parse_addnames(placeNameTag, rest)
    if hasNoAddN:
        text = BeautifulSoup(hasNoAddN).get_text()
    else:
        text = BeautifulSoup(rest).get_text()

    # Index-refs + mentionings
    text, indexRefsTag = find_index_refs(text)
    text, ment = parse_mentionings(text)
    
    # Settlement type, reference-point, district, region, country
    settlementKeys = 'Dorf|Stadt|Stadtteil|Burg|ehem. Burg|Hofgut|Hof|Vogtei'\
                 '|Ort|.rtlichkeit|Gemeinde|Kloster|Abtei|Schloss|Herrschaft'\
                 '|Gft\.|Kgr\.|Land|Kgr\.|Herzogtum|Hzgt\.|Grafschaft|Bistum'\
                 '|F.rstentum|Deutschordenskommende|Zisterzienserabtei|M.hle'\
                 '|Hochstift|Pfarrei|Erzstift|Erzbistum|Dekanat|Burgsiedlung'\
                 '|Domstift|Reichsland|Deutschordensballei|Wasserburg|Region'\
                 '|Regierungssitz|Deutschordenshaus|Gebiet|Gde\.|Reichsstadt'\
                 '|lothr\. Amt'
    settlement = '(?:' + settlementKeys + ')(?![\w])'
    settleMatch = re.match('(?u)(.*?)('+ settlement +')(.*?)', text)
    
    if settleMatch:
        placeNameTag, index = annotate_groupnames(settleMatch, placeNameTag)
        text = text[index:]
        settleTag['type'] = settleMatch.group(2)
    else:
        settleTag['type'] = 'unknown'
    
    placeNameTag = parse_place_name(placeNameTag, text)
    
    headerTag.append(placeNameTag)
    
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)
    
    return name.rstrip(', '), headerTag


####################### 3.1.2 Family Header ##################################

def fam_header_to_XML(header):
    '''
    Convert a preprocessed HTML index-item header into an XML family header.
    '''
    headerTag = soup.new_tag('family-header')

    # Name
    name = header.b.get_text()
    famNameTag = soup.new_tag('family-name')
    nameTag = soup.new_tag('name')
    famNameTag.append(nameTag)
    nameTag.append(name)
    
    hasNoB = del_b_tag(header)
    

    # Alternative names
    famNameTag, hasNoAddN = parse_addnames(famNameTag, unicode(hasNoB))
    headerTag.append(famNameTag)
    
    if hasNoAddN:
        rest = BeautifulSoup(hasNoAddN).get_text()
    else:
        rest = hasNoB.get_text()

    # Location
    parMatch = re.match(r'([^\w]*?)\((.*[A-Za-z][a-z]{1,3}.*)(\), .*)', rest)
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
    
    # Index-refs + mentionings
    t, indexRefsTag = find_index_refs(t)
    rest, ment = parse_mentionings(t)
    
    headerTag.append(rest)
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)

    return name.rstrip(', '), headerTag



#################### 3.1.3 Landmark Header ##################################

def land_header_to_XML(header):
    '''
    Convert a preprocessed HTML index-item header into an XML landmark
    header.
    '''
    headerTag = soup.new_tag('landmark-header')
    geogTag = soup.new_tag('geogName')
    headerTag.append(geogTag)

    # Name
    name = header.b.get_text()
    nameTag = soup.new_tag('name')
    geogTag.append(nameTag)
    nameTag.append(name)
    
    # Alternative names
    hasNoB = del_b_tag(header)

    geogTag, hasNoAddN = parse_addnames(geogTag, unicode(hasNoB))

    if hasNoAddN:
        t = BeautifulSoup(hasNoAddN).get_text()
    else:
        t = hasNoB.get_text()

    headerTag.append(geogTag)

    # Index-Refs + mentionings
    text, indexRefsTag = find_index_refs(t)
    t, ment = parse_mentionings(t)

    # Landmark type
    landKey = 'Fluss|Berg|gau[ ,]|Gau|Bach|Talschaft|Tal|Landschaft|Au'\
              '|Waldung|Wald|Gemeindewald'
    landMatch = re.match('(.*)('+landKey+')(.*)', t)
    
    if landMatch:
        headerTag.append(landMatch.group(1))
        landtype = landMatch.group(2)
        geogTag['type'] = landtype
        headerTag.append(landtype)
        rest = landMatch.group(3)
    else:
        landKey += '|furt|berg'
        landNameMatch = re.search('(.*)('+landKey+')(.*)', name)
        if landNameMatch:
            landtype = landNameMatch.group(2)
            l = landtype.capitalize()
            geogTag['type'] = l
        else:
            geogTag['type'] = 'unknown'
        rest = t

    headerTag.append(rest)

    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)
        
    return name.rstrip(', '), headerTag



#################### 3.1.4 Persongroup Header ################################

def persgr_header_to_XML(header):
    '''
    Convert a preprocessed HTML index-item header into an XML
    persongroup header.
    '''
    headerTag = soup.new_tag('persongroup-header')
    
    text, indexRefsTag = find_index_refs(header.get_text())
    rest, ment = parse_mentionings(text)
    value = header.b.get_text()
    grNameTag = soup.new_tag('group-name')
    headerTag.append(grNameTag)
    grNameTag.append(rest)
    
    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)

    return value.rstrip(', '), headerTag



#################### 3.1.5 Person Header ####################################
    
def pers_header_to_XML(header):
    '''
    Convert a preprocessed HTML index-item header into an XML person
    header. Use hardcoded lists for genName (generational names, e.g.
    senior, the first, junior) and roleName (e.g. duke, king) and
    extern list of forenames (forenameList).
    '''
    headerTag = soup.new_tag('person-header')
    persTag = soup.new_tag('person')
    headerTag.append(persTag)
    global person_id
    persTag['id'] = 'person_'+str(person_id)
    person_id += 1

    # Name
    name = header.b.get_text()
    nameTag = soup.new_tag('persName')
    
    hasNoB = del_b_tag(header)
    
    # Index-Refs + mentionings
    text, indexRefsTag = find_index_refs(header.get_text())
    text, ment = parse_mentionings(text)
    description, ment2 = parse_mentionings(hasNoB.get_text())

    # Forename, surname, genName + roleName
    genNameKeys = 'der .ltere|d\. .ltere|der J.ngere|der Erste|der Zweite'\
                  '|II\.|der Dritte|III\.|IV\.|V\.|VI\.|VII\.|VIII\.|IX\.'\
                  '|Junior|Jr|Senior|Sr|der Junge|der Alte|d\.J\.|I\.|X\.'
    roleKeys = 'K.nig|Kaiser|Herzog|Graf|Hzg\.|Kg\.|Ks\.|Herzogin|Gf\.'\
               '|dt\. Kg\. und r.m\. Ks\.|Gr.fin'
    
    matched = False
    forenameKeys = '|'.join(forenameList)
    
    surForeMatch = re.match('(?u)(?P<surname>[^, ]{3,}?)(, )(?P<forename>' +\
                            forenameKeys + ')([ von]*,? )' , text)
    foreMatch = re.match('(?u)(?P<forename>' + forenameKeys + ')(,)' , text)
    foreSurMatch = re.match('(?u)(?P<forename>' + forenameKeys + ')( )'\
                            '(?P<surname>[^,]{3,})(,)', text)
    foreVonSurMatch = re.match('(?u)(?P<forename>[\w]{3,})( )'\
                               '(?P<surname>von [^,]{3,})(,)', text)
    foreGenRoleMatch = re.match('(?u)(?P<forename>[\w]{3,})( )(?P<genName>' + \
                                genNameKeys + ')(,? ?)(?P<roleName>' + \
                                roleKeys + '?)', text)
    foreGenMatch = re.match('(?u)(?P<forename>[\w]{3,})( )(?P<genName>' + \
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
    
    # description
    if description:
        descriptionTag = soup.new_tag('description')
        persTag.append(descriptionTag)
        descriptionTag.append(description)

    if ment:
        headerTag.append(ment)
    if indexRefsTag:
        headerTag.append(indexRefsTag)
        
    return name.rstrip(', '), headerTag


############################## 3.2 Bodies ####################################

def parse_quotes (htmlitem):
    '''
    Parse quotes in an HTML item. Convert all i-tags into quote-tags.
    Delete all other tags.
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
        if not 'siehe' in quote and not 'Siehe' in quote\
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
    '''Build a concept from a given string, containing name,
       description and mentionings.'''
    soup=BeautifulSoup()
    concTag = soup.new_tag('concept')
    rest, ment = parse_mentionings(text)
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


def rel_conc_to_XML(liste, prefix):
    '''
    Convert a list of strings into a list of concepts, which are added
    to a related-cocepts tag. Identify the current indentation level
    with prefix.
    '''
    relConcTag = soup.new_tag('related-concepts')    
    concList = []
    concTag = None
    for concHTML in liste:
        conc = parse_quotes(concHTML) # TODO: ist das ein html??
        intendMatch = re.match('( *?\-)(.*)', conc)
        if intendMatch:
            concList.append(intendMatch.group(2))
            continue
        elif concList:
            innerRelConcTag = rel_conc_to_XML(concList, prefix + ' -')
            if concTag:
                concTag.append(innerRelConcTag)
            else:
                concTag = innerRelConcTag
            concList = []

        concTag = build_conc_tag(conc)
        relConcTag.append(prefix)
        relConcTag.append(concTag)

    if concList:
            innerRelConcTag = rel_conc_to_XML(concList, prefix + ' -')
            if concTag:
                concTag.append(innerRelConcTag)
            else:
                concTag = innerRelConcTag
            if relConcTag:
                relConcTag.append(concTag)
    
    return relConcTag



################# 3.2.1 ListingBody (FamilyBody, PersongroupBody) ############

def listing_body_to_XML(body):
    '''
    Convert a preprocessed HTML index-item body into an XML
    listing-body. Listing bodies have persons on the first level of 
    indentation. The remaining levels are parsed as concepts.
    '''
    listBodyTag = soup.new_tag('listing-body')
    membersTag = soup.new_tag('members')
    listBodyTag.append(membersTag)

    personList = str(body).split('<br>')
    concList = []
    hyp = ''
    personTag = None
    
    for personHTML in personList:
        person = BeautifulSoup(personHTML)
  
        intendMatch = re.match('( *?\-)(.*)', person.get_text())
        if intendMatch:
            concList.append(intendMatch.group(2))
            continue
            
        elif concList:
            relConcTag = rel_conc_to_XML(concList, ' -')
            if personTag:
                personTag.append(relConcTag)
            concList = []
    
        rest, ment = parse_mentionings(person.get_text())
        personAttrList = rest.split(',')
        #re.split('[,\[]', rest)
        personName=personAttrList[0]
        comma = True
        if '(' in personName and not ')' in personName or '(' in personName and '1' in personName:
            l = personName.split('(')
            personName = l[0]
            print('name: '+personName)
            rest_string = '(' + '('.join(l[1:])
            print('reststring: '+ rest_string)
            copy = personAttrList
            personAttrList = [personName]+[rest_string] + copy[1:]
            print(str(personAttrList))
            comma = False


 #or '[' in personName:
            
        personTag = soup.new_tag('person')
        global person_id
        personTag['id'] = 'person_'+str(person_id)
        person_id += 1
        membersTag.append(personTag)
        nameTag = soup.new_tag('persName')
        personTag.append(nameTag)
        parse_pers_name(nameTag, personName)

        if personName:
            possForename = BeautifulSoup(personName.split()[0]).get_text().\
                           strip(' ()[].,;')
            if possForename != 'Leibeigene' and possForename != 'Herrin' and\
                  possForename != 'Rechtshandlung' and possForename != 'Frau'\
                  and possForename != 'Edelmann':
                if not possForename in forenameList:
                    forenameList.append(possForename)
    
        attrs = ''
        if len(personAttrList)>1:
            possAddName = personAttrList[1]
            if re.match('[ ]'+'(gen\.|den man nennet|dem man sprichet)'
                        +'(.+)', possAddName):
                nameTag.append(', ')
                parse_pers_name(nameTag, possAddName)
                personAttrList = personAttrList[1:]
        
        attrs = ','.join(personAttrList[1:])
        print('attrs: '+attrs)

        persInfoTag = soup.new_tag('description')
        if attrs:
            personTag.append(persInfoTag)
            if comma:
                persInfoTag.append(',')
            persInfoTag.append(attrs)
            print(persInfoTag)
        
        if ment:
            personTag.append(ment)
        
    return listBodyTag


############## 3.2.2 ConceptBody (Location, Landmark, Person) #######

def conc_body_to_XML(body):
    '''
    Convert a preprocessed HTML index-item body into an XML concept
    body, consisting of concepts which recursively contain related
    concepts.
    '''
    listBodyTag = soup.new_tag('concept-body')
    bodyList = str(body).split('<br>')

    if not body.get_text():
        return listBodyTag
    
    relTag = soup.new_tag('related-concepts')
    listBodyTag.append(relTag)
    concList = []
    conceptTag = None
    for conceptHTML in bodyList:
        concept=parse_quotes(conceptHTML)
        
        intendMatch = re.match('( *-)(.*)', concept)
        if intendMatch:
            if intendMatch.group(2).strip().startswith('-')\
                    and not concList:
                print intendMatch.group(2)
                raise ExtractorException('Ill-formed HTML (body): '\
                      'unexpected indentation level in inner related concept')
            concList.append(intendMatch.group(2))
            continue
            
        elif concList:
            relConcTag = rel_conc_to_XML(concList, ' -')
            conceptTag.append(relConcTag)
            concList = []
    
        conceptTag=build_conc_tag(concept)
        relTag.append(conceptTag)
 
    if concList:
            relConcTag = rel_conc_to_XML(concList, ' -')
            if conceptTag:
                conceptTag.append(relConcTag)
            else:
                raise ExtractorException('Ill-formed HTML (body): '\
                      'unexpected indentation level in related concept')

    return listBodyTag


############################ 4. Parser ##################################

############################ 4.1 Familiy Parser    #####################

def fam_to_XML(family, id):
    '''
    Convert a preprocessed HTML index item into a completely annotated
    XML family item.
    '''
    itemTag = soup.new_tag('item')
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
    '''
    Convert a preprocessed HTML index item into a completely annotated
    XML persongroup item.
    '''
    itemTag = soup.new_tag('item')
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
    '''
    Convert a preprocessed HTML index item into a completely annotated
    XML person item.
    '''
    itemTag = soup.new_tag('item')
    value, itemHeader = pers_header_to_XML(person.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'person'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = conc_body_to_XML(person.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    
    
################## 4.4 LocationParser #############

def loc_to_XML(location, id):
    '''
    Convert a preprocessed HTML index item into a completely annotated
    XML location item.
    '''
    itemTag = soup.new_tag('item')
    value, itemHeader = loc_header_to_XML(location.header)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'location'
    itemTag['value'] = value
    itemTag.append(itemHeader)
    itemBody = conc_body_to_XML(location.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag
    
    
################## 4.5 LandmarkParser #############

def land_to_XML(landmark, id):
    '''
    Convert a preprocessed HTML index item into a completely annotated
    XML landmark item.
    '''
    itemTag = soup.new_tag('item')
    value, itemHeader = land_header_to_XML(landmark.header)
    itemTag.append(itemHeader)
    itemTag['id'] = 'item_'+str(id)
    itemTag['type'] = 'landmark'
    itemTag['value'] = value
    itemBody = conc_body_to_XML(landmark.body)
    itemTag.append(itemBody)
    #print(value)
    return itemTag

##########################################################

def build_header_body(h, b, lineList):
    '''
    Merges refering lines into the header.
    '''
    if len(lineList) > 0:
        firstLineText=BeautifulSoup(lineList[0]).get_text().strip()
        
        if firstLineText.startswith(('siehe', 'mit siehe', 'vgl.')):
            h += lineList[0]
            lineList = lineList[1:]
            h, b = build_header_body(h, b, lineList)
         
        else:
            b = '<br>'.join(lineList)
    return (h, b)



def extract_items():
    '''
    Locate the index in the HTML file. Split it up into enties realised
    as IndexItems. Divede items into header and body.
    '''
    text = ''
    t = ''

    with codecs.open('html/sbr-regesten.html', 'r', 'cp1252') as f:
        text = f.read()
        text = unicode(text)
        t2 = text.replace('\n',' ')
        t = t2.replace('\r','')

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

                h = '<itemHeader>' + h + '</itemHeader>'
                b = '<itemBody>' + b + '</itemBody>'
                header = BeautifulSoup(h)
                body = BeautifulSoup(b)
                item = IndexItem(header, body)
                items.append(item)
                
    return indexTag, items


########################################################

def classify_and_parse(items):
    '''
    Decide for each HTML item in a list if it is a location, family,
    person, landmark or persongroup. Parse them accordingly. Append
    items classified as "siehe" without parsing them. Return a list
    of XML items and HTML-siehe-items. Hardcoded lists of keys for
    families, locations, persons, persongroups and landmarks are 
    used for classification.
    '''

    xmlItems = []
    id = 0

    for item in items:
        header = item.header.get_text()
        
        famMatch = re.search('[Ff]amilie|Adelsgeschlecht', header)
        
        locMatch = re.search('[Ss]tadt,|Stadtteil|Dorf|Burg |Hof |Hofgut|'\
                             'Gemeinde |Ort |.rtlichkeit |Kloster|Schloss|'\
                             'Herrschaft|Gft\.|Kgr\.|Region|Gebiet|Abtei|'\
                             'Land |Kgr\.|Herzogtum|Hzgt\.|[Gg]rafschaft|'\
                             'F.rstentum|Deutschordenskommende|RLP|M.hle|'\
                             'Bistum|Vogtei|Regierungssitz|Hochstift|Gde\.|'\
                             'Pfarrei|W.stung|F\)|Erzstift|, Erzbistum|'\
                             'Dekanat|Domstift|Reichsland|Wallfahrt|'\
                             'Land |Reise|lothr. Amt|Deutschordensballei|'\
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
            x = loc_to_XML(item, id)
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
            x = land_to_XML(item, id)
            xmlItems.append(x)
            landmarks.append(item)

        elif sieheMatch:
            siehe.append(id)
            item.header['tmp_id'] = id
            xmlItems.append(item)
            
        else:
            unclassified.append(item)
            id -= 1
        
        id += 1
    return xmlItems


#########################################

def postprocess_siehe(items):
    '''
    Postprocess a list of items. Solves references in the headers of
    yet unresolved siehe-items to find out their type. Tag them and add
    them to the complete list of xml items.
    '''
    xmlItemsComplete = []
    
    for item in items:
        if not isinstance(item, IndexItem):
            xmlItemsComplete.append(item)
        else:
            type = None
            line = item.header.get_text()
            sieheMatch = re.search('siehe (.*)',line)
            if sieheMatch:
                n = sieheMatch.group(1).strip().split('/')[0]
                itemTag = soup.new_tag('item')
                for i in items:
                    if not isinstance(i, IndexItem):
                        if n in i['value'].strip():
                            type = i['type']
                            itemTag['type'] = type
                            itemTag['value'] = item.header.b.get_text()
                            itemTag['id'] = 'item_' + \
                                                  str(item.header['tmp_id'])
                            if not type:
                              print (value+': unknown type.')
                                
                            if type == 'location':
                              settleType = i.find('location-header').placeName\
                                            .settlement['type']
                              value, header = loc_header_to_XML(item.header)
                              header.placeName.settlement['type'] = settleType
                              itemTag.append(header)
                              itemTag.append(conc_body_to_XML(item.body))
                                
                            if type == 'family':
                              value, header = fam_header_to_XML(item.header)
                              itemTag.append(header)
                              itemTag.append(listing_body_to_XML(item.body))

                            xmlItemsComplete.append(itemTag)
                            break
    return xmlItemsComplete


########################## 5. index_to_xml    ################################

def index_to_xml():
    '''
    Main function. Find the index in the HTML file, convert it into XML
    and write into index.xml.
    '''
    print('Index Extractor is working ..')
    
    indexTag, items = extract_items()        
    items = classify_and_parse(items)
    xmlItemsComplete = postprocess_siehe(items)

    with codecs.open ('resources/forenames.txt', 'w', 'utf-8') as file:
        file.write('\n'.join(forenameList))
        
    with open ('index.xml', 'w') as file:
        for item in xmlItemsComplete:
            indexTag.append(item)
            indexTag.append('\n')
        file.write(indexTag.encode('utf-8'))
    
    print('Index converted into xml.')