# Raw material for CSV <-> KML
import csv
import datetime
import sys
import re

# To make it easier to pretty print the XML, use lxml instead of ElementTree.
# sudo apt install python3-pip
# pip install lxml
from lxml import etree # type: ignore

show_stats = False

def log(message):
    script_name = sys.argv[0]
    print(str(datetime.datetime.now()) + '\t'+ script_name + ': ' + message)

class Sorter:
    field_indices = {}
    field_names_dict = {}

    def read_from_stream_into_dict(self, file_name, output_file):
        dict = {}
        fieldnames = None
        with open(file_name, 'r', newline='') as infile:
            reader = csv.DictReader(infile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            fieldnames = reader.fieldnames
            for record in reader:
                if record.get('geo_coord_UTM'):
                    dict[record['resource_name']] = record
        if output_file == 'calced':
            log(str("{: >4d}".format(len(dict))) + ' records read from ' + file_name)
        return fieldnames, dict 

    def get_record_key(self, array_record):
        return array_record[self.field_indices['year']] + ' ' + array_record[self.field_indices['resource_name']]

    def to_array(self, dict_record):
        arr = []
        for key, value in dict_record.items():
            arr.insert(self.field_indices[key], value)
        return arr

    def to_dict(self, array_record):
        dict_record = {}
        i = 0
        for v in array_record:
            dict_record[self.field_names_dict[i]] = v
            i += 1
        return dict_record

    def do_sort(self, tree):
        kml = tree.getroot()
        document = kml[0]
        dict = {}
        for placemark in document:
            dict[placemark[0]] = placemark
        print("# of points: " + str(len(dict)))

    def write_kml_file(fn, root):
        with open(fn, 'w') as kml_file:
            kml_file.writelines('<?xml version="1.0" encoding="UTF-8"?>\n')
            bytes = etree.tostring(root, pretty_print=True)
            kml_file.write(bytes.decode("utf-8"))

    def main(self):
        # Read in KML, sort by name, write out KML and site count
        fn = "./sites.kml"
        tree = etree.parse(fn)
        self.do_sort(tree)
        # self.write_kml_file(fn, root)

if '__main__' == __name__:
    Sorter().main()
