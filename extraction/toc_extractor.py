""" This module extracts the table of contents of the Sbr Regesten. """

import codecs
from bs4 import BeautifulSoup

text = codecs.open('../html/sbr-regesten.html', 'r', 'cp1252').read()
soup = BeautifulSoup(text)

toc = []

inside_toc = False

for line in soup.get_text().split('\n'):
    if not inside_toc:
        if line.startswith('Inhaltsverzeichnis'):
            inside_toc = True
            toc.append(line)
    else:
        if line.startswith('Vorwort'): break
        if not u'\xa0' in line: toc.append(line)

def write_with_indent(file, string, indent_level):
    spaces = indent_level * ' '
    file.write(spaces+string)


with codecs.open('../sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
    write_with_indent(xmlfile, '<toc>\n', 2)
    for line in toc:
        write_with_indent(xmlfile, line+'\n', 4)
    write_with_indent(xmlfile, '</toc>\n', 2)
