import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import pandas as pd
import schema
OSM_PATH = "sample.osm"
NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    mapping = { 
            "Ave":"Avenue",
            "Rd":"Road",
            "Blvd":"Boulevard",
            "court":"Court"
            }
    def update_name(name, mapping):
        m = street_type_re.search(name)
        x = m.group()
        if x in mapping.keys():
            name = name.strip(x)
            name = name + mapping[x]
            
        return name
    
    def update_postcode(postcode):
        split_post = postcode.split("-")
        return split_post[0]
    
    def get_tags(element,child,tags):
        
        tag_dict ={}
        tag_dict['id']=element.attrib['id']
        tag_dict['value']= child.attrib['v']      
            
        if problem_chars.search(child.attrib['k']):
            return tags
        elif ":" not in child.attrib['k']:
            tag_dict['key']=child.attrib['k']
            tag_dict['type']= default_tag_type
        elif ":" in child.attrib['k']:
            split_type = child.attrib['k'].split(':',1)
            tag_dict['type']=split_type[0]
            tag_dict['key']=split_type[1]
            if child.attrib["k"] == 'addr:street':
                
                tag_dict["value"] = update_name(child.attrib["v"], mapping)
            if child.attrib["k"] == 'addr:postcode':
                    if child.attrib["v"].find("-"):
                        #print child.attrib["v"]
                        tag_dict["value"] = update_postcode(child.attrib["v"])
                        #print tag_dict["value"]
                    else:
                        tag_dict["value"] = child.attrib["v"]    
                        
                #uncomment to notice changes in name
                #print tag_dict["value"]
        
        tags.append(tag_dict)
        return tags
        
        
    if element.tag == 'node':
        
        for i in node_attr_fields:
            
            node_attribs[i]=element.attrib[i]
        
        for child in element.iter('tag'):
            tags = get_tags(element,child,tags)
            
        
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i]=element.attrib[i]
        count = 0
        for child in element.iter("nd"):
            way_dict={}
            way_dict['id']=element.attrib['id']
            way_dict['node_id']=child.attrib['ref']
            way_dict['position'] = count
            count+=1
            way_nodes.append(way_dict)
        for child in element.iter('tag'):
            tags = get_tags(element,child,tags)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                    
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=False)