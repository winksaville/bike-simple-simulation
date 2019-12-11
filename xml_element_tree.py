#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp

from typing import Optional, Tuple

def parseTag(tag: str) -> Tuple[Optional[str], str]:
    "Return ns, name"
    if tag[0] == '{':
        ns, name = tag[1:].split("}")
    else:
        ns, name = Tuple[None, tag]
    return ns, name

def prtElement(level: int, elem: et.Element) -> None:
    if elem is None:
        return None

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
        print('recurse')
        prtElement(level+indent, subElem)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Display gpx trkpt's.")
    parser.add_argument('filename', type=str, help='gpx file to process')
    args = parser.parse_args()
    print(f'filename={args.filename}')

    elem_trkpt: et.Element
    tree = et.parse(args.filename)
    root: et.Element = tree.getroot()

    print('root:')
    prtElement(0, root)
    print('root: DONE')

    print('trkpts:')
    #for elem_trkpt in root.findall('./{*}trk/{*}trkseg/{*}trkpt'):
    for elem_trkpt in root.findall('.//{*}trkpt'):
        prtElement(0, elem_trkpt)
    print('trkpts: DONE')
