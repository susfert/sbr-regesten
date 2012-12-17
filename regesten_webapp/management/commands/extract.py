"""
This module makes extraction pipeline available as a Django management
command.

Author: Tim Krones <tkrones@coli.uni-saarland.de>
"""

from django.core.management.base import NoArgsCommand
from extraction import regest_extractor, index_extractor

class Command(NoArgsCommand):
    help = 'Starts the extraction process for regests and index entries'

    def handle_noargs(self, **options):
        regest_extractor.extract_regests()
        index_extractor.extract_index()
