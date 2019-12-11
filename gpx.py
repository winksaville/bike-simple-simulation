#!/usr/bin/env python3

# bike power calculation
import math
import numpy as np
import xml.etree.ElementTree as et
import track_point as tp
import re

#from __future__ import annotations
from typing import Any, Union, Optional, Tuple, Pattern, Match

tree = et.parse('RAAM_TS00_route_snippet.gpx')
root: et.Element = tree.getroot()
print(f'root.tag={root.tag}')
print(f'root.attrib={root.attrib}')

def parseTag(tag: str) -> Tuple[Optional[str], str]:
    "Return ns, name"
    if tag[0] == '{':
        ns, name = tag[1:].split("}")
    else:
        ns, name = Tuple[None, tag]
    return ns, name

def prtElement(level: int, elem: et.Element) -> None:
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
elem_trkpt: et.Element
for elem_trkpt in root.findall('.//{*}trkpt'):
    prtElement(0, elem_trkpt)

print('track points: DONE')

pt1 = tp.TrackPoint()
print(f'pt1={pt1}')

re_float: str = r'[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?'
pi_str: str = '3.14159'
cre_num: Pattern = re.compile(re_float)
# How to define a user type for Optional[Match[str]]???
pi_match_obj: Optional[Match[str]] = cre_num.match(pi_str)
print(f'cre_num.match({pi_str})={pi_match_obj}')
if pi_match_obj:
    pi_match_obj_group = pi_match_obj.group()
    print(f'pi_match.group()=={pi_match_obj_group}')
    assert(pi_match_obj_group == pi_str)

re_trkpt_lat_lon_attr: str = r'{\'lat\': \'(?P<lat>' + re_float + r')\', \'lon\': \'(?P<lon>' + re_float + r')\'}'
cre_trkpt_lat_lon_attr: Pattern = re.compile(re_trkpt_lat_lon_attr)

lat_lon_attr_str: str = r"{'lat': '1.0e1', 'lon': '-2.0e-1'}"
lat_lon_match_obj: Optional[Match[str]] = cre_trkpt_lat_lon_attr.match(lat_lon_attr_str)
print(f'lat_lon_match_obj={lat_lon_match_obj}')
if lat_lon_match_obj:
    lat_str: str
    lon_str: str
    lat_str, lon_str = lat_lon_match_obj.group('lat', 'lon')
    print(f'lat_str={lat_str}, lon_str={lon_str}')
    lat=float(lat_str)
    lon=float(lon_str)
    print(f'lat={lat}, lon={lon}')

def parse_trkpt_attrib(elem) -> Tuple[Optional[str], str]:
    "Return lat, lon"
    if elem.attrib[0] == '{':
        ns, name = elem[1:].split("}")
    else:
        ns, name = None, elem
    return ns, name

def gpx_trkpt_to_TrackPoint(elem_trkpt: et.Element) -> tp.TrackPoint:
    return tp.TrackPoint()

print('TrackPoints:')
for elem_trkpt1 in root.findall('.//{*}trkpt'):
    pt = gpx_trkpt_to_TrackPoint(elem_trkpt)
    print(f'pt={pt}')
print('TrackPoints: DONE')
