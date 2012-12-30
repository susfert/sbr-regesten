# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys
from regesten_webapp import models
from regesten_webapp.models import Location, Family, Person, Region, PersonGroup, Landmark, Concept, IndexEntry, Regest, RegestDate #*

countConc=2000


def ment_to_db(xmlNode, concept): # TODO
    ''' TODO: Extracts related regests and writes them into the database. To be done when the regests are extracted.'''
    pass
    '''if hasattr(xmlNode, 'mentioned-in'):
      for reg_ref in xmlNode.find('mentioned-in'):
        if isinstance(reg_ref, NavigableString):
          continue
        else:
          titleList=RegestTitle.objects.filter(title__startswith=reg_ref.get_text().strip())
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
        #print(node.get_text())
        return node.get_text()
    else:
        return ''


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
    return p
  
def create_concept(xmlNode):
    ''' Creates a concept. '''
    c = Concept()
    c.name = xmlNode.name
    return c


def relconc_to_db(relConc, createElement=create_concept):
    '''Extracts related-concepts and writes them into the database.'''
    global countConc
    clist = []
    if relConc:
        for conc in relConc:
            if isinstance(conc, NavigableString):
                continue
            if conc.name == 'concept' or conc.name == 'person':
                c = createElement(conc)
                c.xml_repr = conc
                countConc += 1
                c.save()
                ment_to_db(conc, c)
                if hasattr(conc, 'related-concepts'):
                    add_all(c.related_concepts, relconc_to_db(conc.find('related-concepts')))
                    clist.append(c)
    return clist



def loc_to_db(itemsoup):
    '''Extracts a location and writes it into the database.'''
    l=Location()
    placeName=itemsoup.find('location-header').placename
    attrs=placeName.settlement.attrs
     
    # Name & Additional names
    if placeName.addNames:
        l.additional_names = placeName.addNames
    else:
        l.additional_names = ''
    l.name = itemsoup['value']
        
    # Wuestungen
    if 'type' in attrs:
        l.location_type = placeName.settlement['type']
    vill = placeName.settlement['w']
    if vill=='true':
       l.abandoned_village = True
       l.av_ref = placeName.settlement['w-ref']
    else:
       l.abandoned_village = False    
        
      
    # Reference point & District
    point=placeName.find('reference_point')
    if point:
        point=point.get_text().strip(' ,;.')
    if point:
        l.reference_point = point
    else:
        l.reference_point = ''
    if placeName.district:
        l.district = placeName.district.get_text().strip(' ,;.')
      
    # Region & Country
    if placeName.region:
        regs = Region.objects.filter(name=placeName.region.get_text().strip(' ,;.'))
        if regs:
            region = regs[0]
        else:
            region = Region.objects.create(name=placeName.region.get_text().strip(' ,;.'), region_type=placeName.region['type'])
        l.region = region
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
        if unicode(placeName.country.get_text()) == u'Tuerkei': # TODO
            l.country = u'Tuerkei'
        if placeName.country.get_text() == "Spanien":
            l.country = "Spanien"
        if placeName.country.get_text() == "It":
            l.country = "Italien"
    # all Bundeslaender are in Deutschland by definition, although this information is not included in the original Regesten
    elif l.region and l.region.region_type == 'Bundesland':
        l.country = "Deutschland"
        
        
    # ID
    #l.id=itemsoup['id'].split('_')[1]
    l.save()
    
    # mentioned_in
    ment_to_db(itemsoup.find('location-header'), l)
    
    # related concepts
    if itemsoup.find('concept-body'):#.get_text():
        add_all(l.related_concepts, relconc_to_db(itemsoup.find('concept-body').find('related-concepts')))
       
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
   
    # ID
    #land.id=itemsoup['id'].split('_')[1]
    land.save()
       
    # mentioned_in
    ment_to_db(itemsoup.find('landmark-header'), land)
 
    # related concepts
    if hasattr(itemsoup, 'concept-body'):
        add_all(land.related_concepts, relconc_to_db(itemsoup.find('concept-body').find('related-concepts')))
       
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
        #print(if_exists(header.person.description.get_text()))
        p.description = if_exists(header.person.description)

        # ID
        #p.id=itemsoup['id'].split('_')[1]
        p.save()
            
        # mentioned_in
        ment_to_db(itemsoup.find('person-header'), p)
        
        # related concepts
        if hasattr(itemsoup, 'concept-body'):
            add_all(p.related_concepts, relconc_to_db(itemsoup.find('concept-body').find('related-concepts')))
           
        print (p)
        return p



def persgr_to_db(itemsoup):
    '''Extracts a persongroup and writes it into the database.'''
    pg = PersonGroup()
    header = itemsoup.find('persongroup-header')
     
    # Name
    pg.name = header.find('group-name').get_text()
    
    # ID
    #pg.id=itemsoup['id'].split('_')[1]
    pg.save()
    
    # mentioned_in
    ment_to_db(itemsoup.find('persongroup-header'), pg)
    
    # related-concepts
    if itemsoup.find('listing-body'):
        add_all(pg.members, relconc_to_db(itemsoup.find('listing-body').members, createElement=create_person))
    
    #print('members'+ str(pg.members))
       
    print(pg)
    #pg.save()
    return pg


# writes a family into the database
def fam_to_db(itemsoup):
    '''Extracts a family and writes it into the database.'''
    f = Family()
    header = itemsoup.find('family-header')
     
    # Name & Additional names
    f.name = itemsoup['value'].strip(' ,;.')
    #land.add_Names= TODO
    
    # ID
    #f.id=itemsoup['id'].split('_')[1]
    f.save()
    
    # mentioned_in
    ment_to_db(itemsoup.find('family_header'), f)
    
    # related concepts
    if itemsoup.find('listing-body'):
        add_all(f.members, relconc_to_db(itemsoup.find('listing-body').members, createElement=create_person))
    
    print (f)
    return f
 
 
#  Entry point: writes the XML-index into the database
def index_to_db():
    '''
    Extracts the index items from the sbr-regesten.xml and writes them
    into the database sbr-regesten.db
    '''

    '''for a in [Location, Family, Person, Region, PersonGroup, Landmark, Concept, IndexEntry, Regest, RegestDate]:
      a.objects.all().delete()
      
    r=Regest()
    r.title = RegestTitle.objects.create(title='1290-08-30 (a)')
    r.content = RegestContent.objects.create(content='Dies ist ein Regesten-Content..')
    r.save()
    
    r2=Regest()
    r2.title = RegestTitle.objects.create(title='1290')
    r2.content = RegestContent.objects.create(content='Dies ist ein weiterer Regesten-Content..')
    r2.save()'''
    
    countIndex = 0
    
    with codecs.open ('index32_post.xml', 'r', 'utf-8') as file:
        soup = BeautifulSoup(file)
        #itemList = soup.index.findall('item')
        itemList = soup.findAll('item')
        
        
        for itemsoup in itemList:
            #soup=BeautifulSoup(item)
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
      
      
            i = IndexEntry()
            #i.defines = entry
            i.xml_repr = itemsoup
            i.id = entry.id
            #i.id = countIndex
            countIndex += 1
            #i.save()