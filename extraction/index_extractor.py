from regesten_webapp import models
from index_to_xml import *
from index_to_db import *
from index_xml_postprocess import *


def extract_index():
 index_to_xml()
 #index_to_xml()
 index_xml_postprocess()
 index_to_db()
