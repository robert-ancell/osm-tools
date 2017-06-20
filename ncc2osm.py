#!/usr/bin/python

# I used this script to convert Napier City Council building outlines into .osm format for manual import

import sys
from pyproj import Proj, transform
from lxml import etree

if len (sys.argv) < 2:
    print 'Usage: ' + sys.argv[0] + ' <file>'
    sys.exit (1)

inProj = Proj(init='epsg:2108')
outProj = Proj(init='epsg:4326')

doc = etree.fromstring (file (sys.argv[1]).read ())
nodes = {}
ways = []
height = None
id = 1
for element in doc.iter ():
    if element.tag == '{NCC}BUILDINGS':
        height = None
    elif element.tag == '{NCC}BLD_HEIGHT':
        height = element.text
    elif element.tag == '{http://www.opengis.net/gml}coordinates':
        way_nodes = []
        for n in element.text.split (' '):
            x1, y1 = n.split (',')
            lon, lat = transform (inProj, outProj, x1, y1)
            try:
                (n, _, _) = nodes[(lat, lon)]
            except KeyError:
                n = id
                id += 1
                nodes[(lat, lon)] = (n, lat, lon)
            way_nodes.append (n)
        tags = [('building', 'true')]
        if height is not None:
            tags.append (('height', height))
        ways.append ((id, way_nodes, tags))
        id += 1

print '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>'
print '<osm version="0.6" generator="ncc2osm">'
for (id, lat, lon) in nodes.values ():
        print '  <node id="' + str (id) + '" lat="' + str (lat) + '" lon="' + str (lon) + '" visible="true" version="1"/>'
for (id, nodes, tags) in ways:
    print '  <way id="' + str (id) + '" visible="true" version="1">'
    for n in nodes:
        print '    <nd ref="' + str (n) + '"/>'
    for (key, value) in tags:
        print '    <tag k="' + key + '" v="' + value + '"/>'
    print '  </way>'
print '</osm>'
