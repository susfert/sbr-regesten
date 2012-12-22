# -*- coding: utf-8 -*-
""" This module extracts the list of abbreviations of the Sbr Regesten. """

import codecs, re
from bs4 import BeautifulSoup

text = codecs.open('../html/sbr-regesten.html', 'r', 'cp1252').read()
soup = BeautifulSoup(text)

abbrevs = []

inside_abbrevs = False

for line in soup.get_text().split('\n'):
    if not inside_abbrevs:
        if line.startswith(u'Abkürzungen'):
            inside_abbrevs = True
            abbrevs.append(line)
    else:
        if line.startswith('Siglen'): break
        if not u'\xa0' in line and not re.match(' *$', line):
            if re.match(' +', line):
                abbrevs[-1] += ' ' + line.strip()
            else:
                abbrevs.append(line)

def write_with_indent(file, string, indent_level):
    spaces = indent_level * ' '
    file.write(spaces+string)


with codecs.open('../sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
    write_with_indent(xmlfile, '<abbrev-list>\n', 2)
    for number, line in enumerate(abbrevs):
        if number % 2 == 0:
            if number == 0:
                write_with_indent(xmlfile, line+'\n', 4)
            else:
                write_with_indent(xmlfile, '<entry>\n', 4)
                write_with_indent(xmlfile, '<abbr>'+line+'</abbr>', 6)
        elif not number % 2 == 0:
            if number == 1:
                write_with_indent(xmlfile, '<list-info>'+line+'</list-info>\n', 4)
            else:
                write_with_indent(xmlfile, '<expan>'+line+'</expan>\n', 0)
                write_with_indent(xmlfile, '</entry>\n', 4)
    write_with_indent(xmlfile, '</abbrev-list>\n', 2)
