"""
This module extracts the index from the Sbr Regesten.

Author: Susanne Fertmann <s9sufert@stud.uni-saarland.de>
"""


from regesten_webapp import models
from index_to_xml import *
from index_to_db import *
from index_xml_postprocess import *


def extract_index():
 #index_to_xml()      # extracts forenames
 index_to_xml()
 index_xml_postprocess()
 index_to_db()


