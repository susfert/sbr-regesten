'''from regesten_webapp import models

def extract_index():
    pass'''

from bs4 import BeautifulSoup, Tag, NavigableString
import codecs, string, re, sys
from regesten_webapp import models
from regesten_webapp.models import Location, Family, Person, Region, PersonGroup, Landmark, Concept, IndexEntry, Regest, RegestDate #*

countConc=2000

# Writes the mentionings (related regests) into the DB.
def mentToDB(xmlNode, concept):
  pass
  '''if hasattr(xmlNode, 'mentioned-in') and xmlNode.find('mentioned-in'):
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


def addAll(obj, li):
  for elem in li:
    obj.add(elem)

def createPerson(xmlNode):
  p= Person()
  p.name = xmlNode.find('name').get_text()
  return p
  
def createConcept(xmlNode):
  c=Concept()
  c.name = xmlNode.find('name').get_text()
  return c

# writes related_concepts (list of concepts) into the database
def relConcToDB(relConc, createElement=createConcept):
  global countConc
  clist=[]
  if relConc:
    for conc in relConc:
      if isinstance(conc, NavigableString):
        continue
      if conc.name=='concept' or conc.name=='person':
        c=createElement(conc)
        countConc+=1
        c.save()    
        mentToDB(conc, c)
        if hasattr(conc, 'related_concepts'):
          addAll(c.related_concepts, relConcToDB(conc.related_concepts))
        clist.append(c)
  return clist


# writes a location into the database
def locToDB(soup):
    l=Location()
    placeName=soup.indexitem.find('location-header').placename
    attrs=placeName.settlement.attrs
     
    # Name & Additional names
    l.add_Names=placeName.addNames
    l.name=soup.indexitem['value']
        
    # Wuestungen
    if 'type' in attrs:
      l.location_type = placeName.settlement['type']
    l.abandoned_village = placeName.settlement['w']
    if l.abandoned_village==True:
      l.av_ref = placeName.settlement['w-ref']
      
    # Reference point & District
    point=placeName.find('reference_point')
    if point:
     l.reference_point = point
    else:
     l.reference_point = ''
    l.district = str(placeName.district.get_text())
      
    # Region & Country
    if placeName.region: # funktioniert noch nicht, da Typ obligatorisch
      region = Region.objects.create(name=placeName.region.get_text(), region_type='Bundesland') # TODO region_type!!!
      l.region = region
    if placeName.country:
      l.country = placeName.country
        
    # ID
    #l.id=soup.indexitem['id'].split('_')[1]
    l.save()
    
    # mentioned_in
    mentToDB(soup.indexitem.find('location-header'), l)
    
    # related concepts
    if soup.indexitem.find('concept-body').get_text():
      addAll(l.related_concepts, relConcToDB(soup.indexitem.find('concept-body').related_concepts))
       
    print(l)
    return l
  

# writes a landmark into the database
def landToDB(soup):
    land=Landmark()
    header=soup.indexitem.find('landmark-header')
     
    # Name & Additional names
    land.name=soup.indexitem['value']
    if header.geogname:
      land.add_Names= header.geogname
      
      land.landmark_type=str(header.geogname['type'])
   
    # ID
    #land.id=soup.indexitem['id'].split('_')[1]
    land.save()
       
    # mentioned_in
    mentToDB(soup.indexitem.find('landmark-header'), land)
 
    # related concepts
    if soup.indexitem.find('concept-body'):
      addAll(land.related_concepts, relConcToDB(soup.indexitem.find('concept-body').related_concepts))
       
    print(land)
    return land
    
  

# writes a landmark into the database
def persToDB(soup):
  #print('perToDB erreicht')
  p=Person()
  if hasattr(soup.indexitem, 'person-header'):
    header=soup.indexitem.find('person-header')
    # Name & Additional names
    p.name=soup.indexitem['value']

    #p.add_Names= TODO
    p.info=header.person.find('person-info')
   
    # ID
    #p.id=soup.indexitem['id'].split('_')[1]
    p.save()
        
    # mentioned_in
    mentToDB(soup.indexitem.find('person-header'), p)
    
    # related concepts
    if hasattr(soup.indexitem, 'concept-body'):
      addAll(p.related_concepts, relConcToDB(soup.indexitem.find('concept-body').related_concepts))
       
    print (p)
    return p


# writes a persongroup into the database
def persGrToDB(soup):
    pg=PersonGroup()
    header=soup.indexitem.find('persongroup-header')
     
    # Name
    pg.name=header.find('group-name').get_text()
    
    # ID
    #pg.id=soup.indexitem['id'].split('_')[1]
    pg.save()
    
    # mentioned_in
    mentToDB(soup.indexitem.find('persongroup-header'), pg)
    
    # related-concepts
    if soup.indexitem.find('listing-body'):
      addAll(pg.related_concepts, relConcToDB(soup.indexitem.find('listing-body').members, createElement=createPerson))
       
    print(pg)
    #pg.save()
    return pg


# writes a family into the database
def famToDB(soup):
    f=Family()
    header=soup.indexitem.find('family-header')
     
    # Name & Additional names
    f.name=soup.indexitem['value']
    #land.add_Names= TODO
    
    # ID
    #f.id=soup.indexitem['id'].split('_')[1]
    f.save()
    
    # mentioned_in
    mentToDB(soup.indexitem.find('family_header'), f)
    
    # related concepts
    if soup.indexitem.find('listing-body'):
      addAll(f.related_concepts, relConcToDB(soup.indexitem.find('listing-body').members, createElement=createPerson))
       
    print(f)
    return f
 
 
#  Entry point: writes the XML-index into the database
def extract_index():
  ''''for a in [Location, Family, Person, Country, Region, PersonGroup, Landmark, Content, Concept, IndexEntry, Regest, RegestTitle, RegestContent, RegestDate]:
    a.objects.all().delete()
    
  r=Regest()
  r.title = RegestTitle.objects.create(title='1290-08-30 (a)')
  r.content = RegestContent.objects.create(content='Dies ist ein Regesten-Content..')
  r.save()
  
  r2=Regest()
  r2.title = RegestTitle.objects.create(title='1290')
  r2.content = RegestContent.objects.create(content='Dies ist ein weiterer Regesten-Content..')
  r2.save()'''
  
  countIndex=0
  
  with open ('allXmlItems.xml', 'r') as file:
    for item in file:
      soup=BeautifulSoup(item)
      type=soup.indexitem['type']

      if type=='location':
        entry=locToDB(soup)
      
      elif type=='family':
        entry=famToDB(soup)
        
      elif type=='person':
        entry=persToDB(soup)
      
      elif type=='persongroup':
        entry=persGrToDB(soup)
      
      elif type=='landmark':
        entry=landToDB(soup)
        
      else:
        entry=''
        print ('unknown type!!')
        break
      
      i=IndexEntry()
      i.defines=entry
      i.xml_repr=item
      #i.id=countIndex
      countIndex+=1
      i.save()
      #print(i)
  
  # Laender-Objekte nur einmal anlegen und evtl aufloesen (F -> Frankreich)
  # XML-Tags entfernen (country, region)