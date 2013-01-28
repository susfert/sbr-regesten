"""
This module extracts the index from the Sbr Regesten.

Author: Susanne Fertmann <s9sufert@stud.uni-saarland.de>
"""

from regesten_webapp import models
from index_utils.index_to_xml import index_to_xml
from index_utils.index_to_db import index_to_db
from index_utils.index_xml_postprocess import index_xml_postprocess


def extract_index():
   index_to_xml()
   index_xml_postprocess()
   index_to_db()


