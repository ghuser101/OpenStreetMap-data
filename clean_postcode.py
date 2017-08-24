"""
cleaning postal code
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample.osm"

def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def update_postcode(postcode):
    split_post = postcode.split("-")
    return split_post[0]

def audit(osmfile):
    osm_file = open(osmfile, "r")
   
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    if tag.attrib["v"].find("-"):
                        #print tag.attrib["v"]
                        updated_postalcode = update_postcode(tag.attrib["v"])
                        print updated_postalcode
                    else:
                        tag_dict["value"] = child.attrib["v"] 
             
                    
    osm_file.close()
    return

if __name__ == '__main__':
    audit(OSMFILE)