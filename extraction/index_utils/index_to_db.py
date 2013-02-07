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
    '''Get consecutive id for an index item'''
    global countIndex
    item_id = countIndex
    countIndex += 1
    return item_id

def ment_to_db(xmlNode, concept): # TODO
    '''
    TO BE IMPLEMENTED:
    Extract related regests and writes them into the database.
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
    '''Add a list of elements to an object.'''
    for elem in li:
          obj.add(elem)


def if_exists(node):
    '''Check if a node exists.'''
    if node:
        return node.get_text().strip(') (')
    else:
        return ''


def create_quote(xmlNode,objId):
    '''Build a quote from XML. Write it into the database.'''
    q = Quote()
    q.content_type = ContentType.objects.get(app_label='regesten_webapp', model='concept')
    q.content = xmlNode.get_text()
    q.object_id = objId
    q.save()
    return q


def create_person(xmlNode):
    ''' Build a person from XML. Write it into the database.'''
    global idConc
    
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
    p.id = idConc
    idConc += 1
    p.save()
    return p

  
def create_concept(xmlNode):
    ''' Build a concept. '''
    name = xmlNode.find('name')
    global idConc
    
    c = Concept()
    c.name = name.get_text()
    c.description = if_exists(xmlNode.description)
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
    '''Extract related-concepts and write them into the database.'''
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
        

def loc_to_db(itemsoup,ref_dict):
    '''Extract a location from XML and write it into the database.'''
    header = itemsoup.find('location-header')
    placeName = header.placename
    attrs = placeName.settlement.attrs
     
    l = Location()
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
    #print(l)
    l.save()
    
    # mentionings + related index entries
    ment_to_db(header, l)
    ref_dict[l.id] = header.find('index-refs')
    
    # related concepts
    if itemsoup.find('concept-body'):
        add_all(l.related_concepts, relconc_to_db(itemsoup.find\
               ('concept-body').find('related-concepts')))
       
    print(l)
    return l
  


def land_to_db(itemsoup,ref_dict):
    '''Extract a landmark from XML and write it into the database.'''
    header = itemsoup.find('landmark-header')
     
    land = Landmark()
    land.name = itemsoup['value']
    if header.geogname:
        land.add_Names = header.geogname
        land.landmark_type = str(header.geogname['type'])
    
    land.id = get_item_ID()
    land.xml_repr = itemsoup
    land.save()
       
    # mentioned_in + related index entries
    ment_to_db(itemsoup.find('landmark-header'), land)
    ref_dict[land.id] = header.find('index-refs')
    
    # related concepts
    if hasattr(itemsoup, 'concept-body'):
        add_all(land.related_concepts, relconc_to_db(itemsoup.find\
                ('concept-body').find('related-concepts')))
       
    print(land)
    return land
    
 
def pers_to_db(itemsoup,ref_dict):
    '''Extract a person from XML and write it into the database.'''
    p = Person()
    #itemsoup.find('person-header')
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
            
        # mentioned_in + related index entries
        ment_to_db(itemsoup.find('person-header'), p)
        ref_dict[p.id] = header.find('index-refs')
        
        # related concepts
        if hasattr(itemsoup, 'concept-body'):
            add_all(p.related_concepts, relconc_to_db(itemsoup.find\
                   ('concept-body').find('related-concepts')))
           
        print (p)
        return p
    else:
        exit()



def persgr_to_db(itemsoup,ref_dict):
    '''
    Extract a persongroup from XML and write it into the database.
    '''
    header = itemsoup.find('persongroup-header')
    
    pg = PersonGroup()
    pg.name = header.find('group-name').get_text()
    pg.id = get_item_ID()
    pg.xml_repr = itemsoup
    pg.save()
    
    # mentioned_in + related index entries
    ment_to_db(itemsoup.find('persongroup-header'), pg)
    ref_dict[pg.id] = header.find('index-refs')
    
    # related-concepts
    if itemsoup.find('listing-body'):
        add_all(pg.members, relconc_to_db(itemsoup.find('listing-body').members\
               , createElement=create_person))
    
    print(pg)
    return pg



def fam_to_db(itemsoup, ref_dict):
    '''Extract a family from XML and write it into the database.'''
    header = itemsoup.find('family-header')
    
    f = Family() 
    f.name = itemsoup['value'].strip(' ,;.')
    f.addnames = if_exists(header.addnames)
    f.id = get_item_ID()
    f.xml_repr = itemsoup
    f.save()
    
    # mentioned_in + related index entries 
    ment_to_db(itemsoup.find('family_header'), f)
    ref_dict[f.id] = header.find('index-refs')
    
    # related-concepts
    if itemsoup.find('listing-body'):
        add_all(f.members, relconc_to_db(itemsoup.find('listing-body').members\
                , createElement=create_person))
    
    print (f)
    return f

 
def items_to_db(itemList):
    '''Add a list of XML index items to the database.'''
    ref_dict = {}
    for itemsoup in itemList:
        type = itemsoup['type']

        if type == 'location':
            entry = loc_to_db(itemsoup,ref_dict)
        
        elif type == 'family':
            entry = fam_to_db(itemsoup,ref_dict)
          
        elif type == 'person':
            entry = pers_to_db(itemsoup,ref_dict)
        
        elif type == 'persongroup':
            entry = persgr_to_db(itemsoup,ref_dict)
        
        elif type == 'landmark':
            entry = land_to_db(itemsoup,ref_dict)
    
        else:
            entry = ''
            print ('unknown type!!')
            break
    return  ref_dict


def isolate_id(id):
    '''Return the number in an id.'''
    return int(id.split('_')[1])


def solve_refs(ref_dict):
'''
Extract references from the dictionary and add them to the database.
'''
    for item_id, refNode in ref_dict.items():
        if refNode:
            refList = [node['itemid'] for node in refNode.findAll('index-ref')]
            objList = [IndexEntry.objects.get(id=isolate_id(ref)) for ref in refList]
            obj = IndexEntry.objects.get(id=item_id)
            add_all(obj.related_entries, objList)



def index_to_db():
    '''
    Extract index items from the XML file and write them into the
    database sbr-regesten.db.
    '''
    print('Writing index into db..')
    
    with codecs.open ('sbr-regesten.xml', 'r', 'utf-8') as file:
        soup = BeautifulSoup(file)
        itemList = soup.find('index').findAll('item')
        
        global countIndex
        countIndex = 0
        global idConc
        idConc = len(itemList) + 1
        
        ref_dict = items_to_db(itemList)
        solve_refs(ref_dict)
