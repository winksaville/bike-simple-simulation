#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np
import xml.etree.ElementTree as et

tree = et.parse('RAAM_TS00_route_snippet.gpx')
root = tree.getroot()
print(f'root.tag={root.tag}')
print(f'root.attrib={root.attrib}')

def parseTag(tag):
    "Return ns, name"
    if tag[0] == '{':
        ns, name = tag[1:].split("}")
    else:
        ns, name = None, tag
    return ns, name

def prtElement(level, elem):
    space = ' '
    indent = 4
    tagNs, tagName = parseTag(elem.tag)
    print(f'{space:<{level}}{tagName}', end = '')
    if elem.attrib:
      print(f' attrib={elem.attrib}', end = '')
    print(':')
    if elem.text and elem.text.strip() != "":
        print(f'{space:<{level+indent}}text="{elem.text}"')
    if elem.tail and elem.tail.strip() != "":
        print(f'{space:<{level+indent}}tail="{elem.tail}"')

    for subElem in elem:
        prtElement(level+indent, subElem)

print('\nroot:')
prtElement(0, root)
print('root: DONE')

print('\ntrack points:')
#for elem_trkpt in root.findall('./{*}trk/{*}trkseg/{*}trkpt'):
for elem_trkpt in root.findall('.//{*}trkpt'):
    prtElement(0, elem_trkpt)

print('track points: DONE')
