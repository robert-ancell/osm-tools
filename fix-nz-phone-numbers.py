# This tool takes an OSM file and corrects invalid / inconsistently formatted
# New Zealand phone numbers.
#
# My method was:
# 1. Use JOSM to download nodes/ways with the phone tag using the Overpass API
# 2. Exported to phone-numbers.osm
# 3. ran this script though it,
# 4. Checked the results made sense manually.
# 5. Loaded phone-numbers-fixed.osm into JOSM
# 6. Uploaded

import xml.etree.ElementTree as ET

tree = ET.parse ('phone-numbers.osm')

def reformat_number (number):
    # Strip out spaces
    stripped = ''
    for c in number:
        if c == ' ' or c == '-':
            continue
        stripped += c
    number = stripped

    if len (number) < 7:
        return None

    # Skip toll-free numbers (for now)
    if number.startswith ('0800') or number.startswith ('0508'):
        prefix = number[:4]
        number = number[4:]
        if len (number) != 6:
            return None
        return prefix + ' ' + number[:3] + ' ' + number[3:]

    # Strip off internation prefix
    if number.startswith ('+64'):
        number = number[3:]
    elif number.startswith ('0064'):
        number = number[4:]
    elif number.startswith ('64 '):
        number = number[3:]

    # Unknown prefix
    if number.startswith ('+'):
        return None

    # Skip unused 0
    if number.startswith ('0'):
        number = number[1:]    
    elif number.startswith ('(0)'):
        number = number[3:]

    # Extract area code
    area_code = ''
    if number.startswith ('('):
        i = number.find (')')
        if i < 0:
            return None
        area_code = number[1:i]
        number = number[i+1:]
    else:
        area_code = number[0]
        number = number[1:]

    # Convert Cell numbers
    if len (number) == 8 and area_code == '2':
        area_code += number[0]
        number = number[1:]

    if len (number) != 7:
        return None

    # Return in format +64 x xxx xxxx
    return '+64 ' + area_code + ' ' + number[:3] + ' ' + number[3:]

def fix_number (parent, element):
    number = element.get ('v')
    fixed = reformat_number (number)
    if fixed == None:
        print number + '?'
    elif fixed != number:
        print number + ' -> ' + fixed
        element.set ('v', fixed)
        parent.set ('action', 'modify')

for e in tree.getroot ():
    if e.tag == 'node':
        for ne in e.getchildren ():
            if ne.tag == 'tag' and ne.get('k') == 'phone':
                fix_number (e, ne)
    elif e.tag == 'way':
        for ne in e.getchildren ():
            if ne.tag == 'tag' and ne.get('k') == 'phone':
                fix_number (e, ne)

tree.write ('phone-numbers-fixed.osm')
