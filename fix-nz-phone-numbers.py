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
    # Blacklist known specially formatted numbers
    if number in ['111', '0508 CANLAW', '0800 83 83 83', '0800 80 50 10', '0800 77 88 98', '0800 30 40 50', '+64 20 100 2000']:
        return number

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
        if len (number) < 6 or len (number) > 7:
            return None
        return prefix + ' ' + number[:3] + ' ' + number[3:]

    # Strip off internation prefix
    if number.startswith ('+64'):
        number = number[3:]
    elif number.startswith ('0064'):
        number = number[4:]
    elif number.startswith ('+064'):
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
        if area_code[0] == '0':
            area_code = area_code[1:]
    else:
        area_code = number[0]
        number = number[1:]

    # Convert Cell numbers
    if area_code == '2':
        area_code += number[0]
        if len (number) < 7 or len (number) > 9:
            return None
        number = number[1:]
        if area_code[1] == '0':
            area_code += number[0]
            number = number[1:]
    else:
        if len (number) != 7:
            return None

    # Return in format +64 x xxx xxxx or +64 x xxxx xxxx
    if len (number) > 7:
        return '+64 ' + area_code + ' ' + number[:4] + ' ' + number[4:]
    else:
        return '+64 ' + area_code + ' ' + number[:3] + ' ' + number[3:]

def reformat_numbers (numbers):
    n = numbers.split (';')
    for i in xrange (len (n)):
        n[i] = reformat_number (n[i])
        if n[i] == None:
            return None
    return ';'.join (n)

def fix_number (parent, element):
    phone = element.get ('v')
    phone_fixed = reformat_numbers (phone)
    if phone_fixed == None:
        print phone + '?'
    elif phone_fixed != phone:
        print phone + ' -> ' + phone_fixed
        element.set ('v', phone_fixed)
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
