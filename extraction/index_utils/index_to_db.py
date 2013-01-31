"""
This module extracts the index from the xml and writes it into the database.

Author: Susanne Fertmann <s9sufert@stud.uni-saarland.de>
"""

# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys
from regesten_webapp import models
from regesten_webapp.models import Location, Family, Person, Region
from regesten_webapp.models import PersonGroup, Landmark, Concept, IndexEntry
from regesten_webapp.models import Regest, RegestDate, Quote, ContentType


def get_item_ID():
    global countIndex
    item_id = countIndex
    countIndex += 1
    return item_id

def ment_to_db(xmlNode, concept): # TODO
    '''
    TODO: Extracts related regests and writes them into the database.
    To be done when the regests are extracted.
    '''
    pass
    '''if hasattr(xmlNode, 'mentioned-in'):
      for reg_ref in xmlNode.find('mentioned-in'):
        if isinstance(reg_ref, NavigableString):
          continue
        else:
          titleList=RegestTitle.objects.filter\
                    (title__startswith=reg_ref.get_text().strip())
          if not len(titleList)==1:
            #print('Keine eindeutige Zuweisung von Regest moeglich.')
            continue
          else:
            print('Regest gefunden!')
            regestList=Regest.objects.filter(title=titleList[0])
            regest=regestList[0]
            con=regest.content
            concept.regestcontent_set.add(con)'''


def add_all(obj, li):
    for elem in li:
          obj.add(elem)


def if_exists(node):
    ''' Checks if a node exists.'''
    if node:
        return node.get_text().strip(') (')
    else:
        return ''


def create_quote(xmlNode,objId):
    '''Creates a quote.'''
    q = Quote()
    q.content_type = ContentType.objects.get(app_label='regesten_webapp', model='concept')
    q.content = xmlNode.get_text()
    q.object_id = objId
    q.save()
    return q


def create_person(xmlNode):
    ''' Creates a name. '''
    p = Person()
    pers_name = xmlNode.persname
    p.name = pers_name.get_text()
    p.additional_names = if_exists(pers_name.addNames)
    p.forename = if_exists(pers_name.forename)
    p.surname = if_exists(pers_name.surname)
    p.maidenname = if_exists(pers_name.maidenname)
    p.rolename = if_exists(pers_name.rolename)
    p.genname = if_exists(pers_name.genname)
    p.description = if_exists(xmlNode.description)
    global idConc
    p.id = idConc
    idConc += 1
    p.save()
    return p
  
def create_concept(xmlNode):
    ''' Creates a concept. '''
    c = Concept()
    name = xmlNode.find('name')
    c.name = name.get_text()
    c.description = if_exists(xmlNode.description)
    global idConc
    c.id = idConc
    idConc += 1
    c.save()

    quoteList = []
    qList = []
    if xmlNode.description:
        quoteList = xmlNode.description.findAll('quote')
    if not isinstance(name, NavigableString):
        quoteList += name.findAll('quote')
    for quote in quoteList:
        q = create_quote(quote, c.id)
        qList.append(q)
    add_all(c.quotes, qList)
    return c


def relconc_to_db(relConc, createElement=create_concept):
    '''Extracts related-concepts and writes them into the database.'''
    clist = []
    if relConc:
        for conc in relConc:
            if isinstance(conc, NavigableString):
                continue
            if conc.name == 'concept' or conc.name == 'person':
                c = createElement(conc)
                c.save()
                ment_to_db(conc, c)
                if hasattr(conc, 'related-concepts'):
                    add_all(c.related_concepts, relconc_to_db(conc.find\
                           ('related-concepts')))
                    clist.append(c)
    return clist


'''def indexrefs_to_db(indexrefs):
      pass'''
        

def loc_to_db(itemsoup):
    '''Extracts a location and writes it into the database.'''
    l = Location()
    header = itemsoup.find('location-header')
    placeName = header.placename
    attrs = placeName.settlement.attrs
     
    # Name & Additional names
    l.additional_names = if_exists(placeName.addNames)
    l.name = itemsoup['value']
        
    # Wuestungen
    if 'type' in attrs:
        l.location_type = placeName.settlement['type']
    vill = placeName.settlement['abandoned-village']
    if vill == 'true':
       l.abandoned_village = True
    else:
       l.abandoned_village = False    
    if 'av-ref' in attrs:
        l.av_ref = placeName.settlement['av-ref']    
      
    # Reference point & District
    ref_point = placeName.find('reference_point')
    if ref_point:
        ref_point = ref_point.get_text().strip(' ,;.')
    if ref_point:
        l.reference_point = ref_point
    else:
        l.reference_point = ''
    if placeName.district:
        l.district = placeName.district.get_text().strip(' ,;.')
    
    # region  
    if placeName.region:
        regs = Region.objects.filter(name=placeName.region.get_text()\
                                    .strip(' ,;.'))
        if regs:
            region = regs[0]
        else:
            region = Region.objects.create(name=placeName.region.get_text()\
                     .strip(' ,;.'), region_type=placeName.region['type'])
        l.region = region

    # country
    if placeName.country:
        if placeName.country.get_text() == "F":
            l.country = "Frankreich"
        if placeName.country.get_text() == "B":
            l.country = "Belgien"
        if placeName.country.get_text() == "CH":
            l.country = "Schweiz"
        if placeName.country.get_text() == "Lux":
            l.country = "Luxemburg"
        if placeName.country.get_text() == "L":
            l.country = "Luxemburg"
        if placeName.country.get_text() == "Spanien":
            l.country = "Spanien"
        if placeName.country.get_text() == "It":
            l.country = "Italien"
    elif l.region and l.region.region_type == 'Bundesland':
        l.country = "Deutschland"

    l.id = get_item_ID()
    l.xml_repr = itemsoup
    l.save()
    
    ment_to_db(header, l)
    
    #if header.find('index-refs'):
        #add_all(l.related_entries, header.find('index-refs'))
    
    if itemsoup.find('concept-body'):
        add_all(l.related_concepts, relconc_to_db(itemsoup.find\
               ('concept-body').find('related-concepts')))
       
    print(l)
    return l
  


def land_to_db(itemsoup):
    '''Extracts a landmark and writes it into the database.'''
    land = Landmark()
    header = itemsoup.find('landmark-header')
     
    # Name & Additional names
    land.name = itemsoup['value']
    if header.geogname:
        land.add_Names = header.geogname
        land.landmark_type = str(header.geogname['type'])
    
    
    land.id = get_item_ID()
    land.xml_repr = itemsoup
    land.save()
       
    # mentioned_in
    ment_to_db(itemsoup.find('landmark-header'), land)
 
    # related concepts
    if hasattr(itemsoup, 'concept-body'):
        add_all(land.related_concepts, relconc_to_db(itemsoup.find\
                ('concept-body').find('related-concepts')))
       
    print(land)
    return land
    
 
def pers_to_db(itemsoup):
    '''Extracts a person and writes it into the database.'''
    p = Person()
    if hasattr(itemsoup, 'person-header'):
        header = itemsoup.find('person-header')
        pers_name = header.person.persname
        
        p.name=itemsoup['value']
        
        p.additional_names = if_exists(pers_name.addNames)
        p.forename = if_exists(pers_name.forename)
        p.surname = if_exists(pers_name.surname)
        p.maidenname = if_exists(pers_name.maidenname)
        p.rolename = if_exists(pers_name.rolename)
        p.genname = if_exists(pers_name.genname)
        p.description = if_exists(header.person.description)
        
        p.id = get_item_ID()
        p.xml_repr = itemsoup
        p.save()
            
        # mentioned_in
        ment_to_db(itemsoup.find('person-header'), p)
        
        # related concepts
        if hasattr(itemsoup, 'concept-body'):
            add_all(p.related_concepts, relconc_to_db(itemsoup.find\
                   ('concept-body').find('related-concepts')))
           
        print (p)
        return p



def persgr_to_db(itemsoup):
    '''Extracts a persongroup and writes it into the database.'''
    pg = PersonGroup()
    header = itemsoup.find('persongroup-header')
     
    # name
    pg.name = header.find('group-name').get_text()
    
    pg.id = get_item_ID()
    pg.xml_repr = itemsoup
    pg.save()
    
    # mentioned_in
    ment_to_db(itemsoup.find('persongroup-header'), pg)
    
    # related-concepts
    if itemsoup.find('listing-body'):
        add_all(pg.members, relconc_to_db(itemsoup.find('listing-body').members\
               , createElement=create_person))
    
    print(pg)
    return pg



def fam_to_db(itemsoup):
    '''Extracts a family and writes it into the database.'''
    f = Family()
    header = itemsoup.find('family-header')
     
    # Name & Additional names
    f.name = itemsoup['value'].strip(' ,;.')
    f.addnames = if_exists(header.addnames)
    
    f.id = get_item_ID()
    f.xml_repr = itemsoup
    f.save()
    
    # mentioned_in
    ment_to_db(itemsoup.find('family_header'), f)
    
    # related concepts
    if itemsoup.find('listing-body'):
        add_all(f.members, relconc_to_db(itemsoup.find('listing-body').members\
                , createElement=create_person))
    
    print (f)
    return f
 
 

def index_to_db():
    '''
    Extracts the index items from the sbr-regesten.xml and writes them
    into the database sbr-regesten.db
    '''
    print('Writing index into db..')
    
    with codecs.open ('sbr-regesten.xml', 'r', 'utf-8') as file:
        soup = BeautifulSoup(file)
        itemList = soup.find('index').findAll('item')
        
        global countIndex
        countIndex = 0
        global idConc
        idConc = len(itemList) + 1
        
        for itemsoup in itemList:
            type = itemsoup['type']

            if type == 'location':
                entry = loc_to_db(itemsoup)
            
            elif type == 'family':
                entry = fam_to_db(itemsoup)
              
            elif type == 'person':
                entry = pers_to_db(itemsoup)
            
            elif type == 'persongroup':
                entry = persgr_to_db(itemsoup)
            
            elif type == 'landmark':
                entry = land_to_db(itemsoup)
        
            else:
                entry = ''
                print ('unknown type!!')
                break
      
      
            #i = IndexEntry()
            #i.xml_repr = itemsoup
            #i.id = entry.id
            #i.id = countIndex
            #countIndex += 1
            #i.save()
            
            
            
            #TODO: erst concepts speichern, dann quotes hinzufuegen!!