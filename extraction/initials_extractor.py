# -*- coding: utf-8 -*-
""" This module extracts the list of initials from the Sbr Regesten. """

import codecs, re
from bs4 import BeautifulSoup

text = codecs.open('html/sbr-regesten.html', 'r', 'cp1252').read()
soup = BeautifulSoup(text)

initials = []

inside_initials = False

for line in soup.get_text().split('\n'):
    if not inside_initials:
        if line.startswith(u'Siglen'):
            inside_initials = True
            initials.append(line)
    else:
        if re.match('\d{4}', line): break
        if not u'\xa0' in line and not re.match(' *$', line):
            if re.match(' +', line):
                initials[-1] += ' ' + line.strip()
            else:
                initials.append(line)

def write_with_indent(file, string, indent_level):
    spaces = indent_level * ' '
    file.write(spaces+string)


def extract_initials():
    with codecs.open('sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
        write_with_indent(xmlfile, '<initials-list>\n', 2)
        for number, line in enumerate(initials):
            if number % 2 == 0:
                if number == 0:
                    write_with_indent(xmlfile, line+'\n', 4)
                else:
                    write_with_indent(xmlfile, '<expan>'+line+'</expan>\n', 0)
                    write_with_indent(xmlfile, '</entry>\n', 4)
            elif not number % 2 == 0:
                write_with_indent(xmlfile, '<entry>\n', 4)
                write_with_indent(xmlfile, '<abbr>'+line+'</abbr>', 6)
        write_with_indent(xmlfile, '</initials-list>\n', 2)
