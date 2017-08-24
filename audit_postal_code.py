"""
Auditing postal code
"""
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def update_postcode(child):
    split_type = child.attrib['v'].split("-")
    return split_post[0]
    


def audit(osmfile):
    osm_file = open(osmfile, "r")
   
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    print tag.attrib['v']
                    
    osm_file.close()
    

if __name__ == '__main__':
    audit(OSMFILE)