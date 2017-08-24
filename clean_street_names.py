import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

mapping = { 
            "Ave":"Avenue",
            "Rd":"Road",
            "Blvd":"Boulevard"    
            }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            
            street_types[street_type].add(street_name)
            #uncomment to get street names
            #print street_name 

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):                
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    #pprint.pprint(dict(street_types))
    return street_types
    

def update_name(name, mapping):
    m = street_type_re.search(name)
    x = m.group()
    name1 = ""
    if x in mapping.keys():
        name = name.strip(x)
        name1 = name + mapping[x]
        

    return name1

def test():
    st_types = audit(OSMFILE)
    #pprint.pprint(st_types)
    

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, mapping)
            print name, "=>", better_name
            if name == "Homestead Rd":
                assert better_name == "Homestead Road"
            if name == "Los Gatos Blvd":
                assert better_name == "Los Gatos Boulevard"

if __name__=='__main__':
    test()
 
    
        