""" This module extracts the front matter part of the Sbr Regesten. """

import codecs
from bs4 import BeautifulSoup

text = codecs.open('html/sbr-regesten.html', 'r', 'cp1252').read()
soup = BeautifulSoup(text)

frontmatter = []

inside_if = False

for line in soup.get_text().split('\n'):
    if not inside_if:
        if '<!--' in line or '[if' in line:
            inside_if = True
            continue
        if line.startswith('Inhaltsverzeichnis'): break
        if line and not line == u'\xa0': frontmatter.append(line)
    else:
        if '[endif]' in line and not '[if' in line:
            inside_if = False


def write_with_indent(file, string, indent_level):
    spaces = indent_level * ' '
    file.write(spaces+string)


def extract_frontmatter():
    with codecs.open('sbr-regesten.xml', 'a', 'utf-8') as xmlfile:
        write_with_indent(xmlfile, '<sbr-regesten>\n', 0)
        write_with_indent(xmlfile, '<frontmatter>\n', 2)
        for line in frontmatter:
            write_with_indent(xmlfile, line+'\n', 4)
        write_with_indent(xmlfile, '</frontmatter>\n', 2)
