# Raw material for CSV <-> KML
import csv
import datetime
import sys
import re

# To make it easier to pretty print the XML, use lxml instead of ElementTree.
# sudo apt install python3-pip
# pip install lxml
from lxml import etree # type: ignore

def log(message):
    script_name = sys.argv[0]
    print(str(datetime.datetime.now()) + '\t'+ script_name + ': ' + message)

class Sorter:

    unknowns = []
   
    def add_unknown(self, placemark):
        unknown = {}
        description = placemark.text[2:placemark.text.find(' - to be located')]
        unknown['name'] = description
        link = re.search(r'\bhttps?://\S+', placemark.text)
        if link:
            unknown['link'] = link.group(0)[0:link.group(0).find(']') - 1]
        else:
            unknown['link'] = ""
        self.unknowns.append(unknown)

    def do_sort(self, tree):
        kml = tree.getroot()
        document = kml[0]
        dict = {}
        knownCount = 0
        unknownCount = 0
        for placemark in document:
            dict[placemark[0].text] = placemark
            if (placemark[0].text.startswith("|")):
                unknownCount += 1
                self.add_unknown(placemark[0])
            else:
                knownCount += 1
        log("# of known points: " + str(knownCount))
        log("# of unknown points: " + str(unknownCount))
        sortedPoints = sorted(dict.items(), key=lambda item: item[0])
        for placemark in document:
            document.remove(placemark)
        for placemark in sortedPoints:
            document.append(placemark[1])

    def write_kml_file(self, fn, tree):
        with open(fn, 'w') as kml_file:
            kml_file.writelines('<?xml version="1.0" encoding="UTF-8"?>\n')
            bytes = etree.tostring(tree, pretty_print=True)
            kml_file.write(bytes.decode("utf-8"))

    def write_unknowns(self):
        with open("unknowns.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "link"])
            for unknown in self.unknowns:
                writer.writerow([unknown['name'], unknown['link']])

    def main(self):
        fn = "./sites.kml"
        tree = etree.parse(fn)
        self.do_sort(tree)
        self.write_kml_file(fn, tree)
        self.write_unknowns()

if '__main__' == __name__:
    Sorter().main()
