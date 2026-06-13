# Raw material for CSV <-> KML
import csv
import datetime
import sys
import re
import urllib.request
from urllib.error import HTTPError, URLError

# To make it easier to pretty print the XML, use lxml instead of ElementTree.
# sudo apt install python3-pip
# pip install lxml
from lxml import etree # type: ignore

def verify_urls(urls):
    """Open each URL and verify it does not return HTTP 404."""
    results = []
    for url in urls:
        print(".", end="", flush=True)
        try:
            request = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(request, timeout=10) as response:
                status = response.getcode()
        except HTTPError as error:
            if error.code == 405:
                # Some servers do not allow HEAD, retry with GET.
                request = urllib.request.Request(url, method='GET')
                with urllib.request.urlopen(request, timeout=10) as response:
                    status = response.getcode()
            else:
                status = error.code
        except URLError as error:
            results.append((url, False, str(error.reason)))
            continue

        if status == 404:
            results.append((url, False, status))
        else:
            results.append((url, True, status))
    print(flush=True)
    return results


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
        URLS = []
        knownCount = 0
        unknownCount = 0
        for placemark in document:
            dict[placemark[0].text] = placemark
            if (placemark[0].text.startswith("|")):
                unknownCount += 1
                self.add_unknown(placemark[0])
            else:
                knownCount += 1
            url = re.search(r'\bhttps?://\S+', placemark[0].text)
            if url:
                url = url.group(0)[0:url.group(0).find(']')]
                URLS.append(url)
        log("# of known points: " + str(knownCount))
        # log("# of unknown points: " + str(unknownCount))
        sortedPoints = sorted(dict.items(), key=lambda item: item[0])
        for placemark in document:
            document.remove(placemark)
        for placemark in sortedPoints:
            document.append(placemark[1])
        results = verify_urls(URLS)
        for url, is_valid, status in results:
            if not is_valid:
                log("Invalid URL: " + url + " (status: " + str(status) + ")")

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
        # self.write_unknowns()

    def test(self):
        URLS = ["https://www.google.com", 
                "https://www.nonexistentwebsite123456789.com",
                "https://photos.app.goo.gl/u563BjuqZ1Hra5zw"]
        results = verify_urls(URLS)
        for url, is_valid, status in results:
            if is_valid:
                log("Valid URL: " + url + " (status: " + str(status) + ")")
            else:
                log("Invalid URL: " + url + " (status: " + str(status) + ")")

    def check_unknowns(self):
        unknowns = [
"https://photos.app.goo.gl/u563BjuqZ1Hra5zw5",
"https://photos.app.goo.gl/YM7FXvxXEuGNhu1j7",
"https://photos.app.goo.gl/eeYpQWW9HZoh6Jkj8",
"https://photos.app.goo.gl/uPF88FFr4bcMt6V87",
"https://photos.app.goo.gl/jeqvCekZqta7EWPq7",
"https://photos.app.goo.gl/r35zq1nDjpz8x7c96",
"https://photos.app.goo.gl/XyvmRfyxmn4qkspaA",
"https://photos.app.goo.gl/iv9DjPrdG2ihHraV7",
"https://photos.app.goo.gl/TY2oKPohRbWeW2xY9",
"https://photos.app.goo.gl/xt1RuE3gCSgPh4wE9",
"https://photos.app.goo.gl/vtp69oYJvY3FGNp66",
"https://photos.app.goo.gl/bm5KJqwh2SgoRuKX7",
"https://photos.app.goo.gl/GdNQAzPqfYUarj5k8",
"https://photos.app.goo.gl/owpwpJ1qczUEMJxb8",
"https://photos.app.goo.gl/6Bny3T1dEAwnhXmC6",
"https://photos.app.goo.gl/XyvmRfyxmn4qkspaA",
"https://photos.app.goo.gl/RkkGYDNsTQKe7K6m8",
"https://photos.app.goo.gl/WbitRXJAfLtLkdkF6"]

        results = verify_urls(unknowns)
        for url, is_valid, status in results:
            if not is_valid:
                log("Invalid URL: " + url + " (status: " + str(status) + ")")

if '__main__' == __name__:
    Sorter().main()
    Sorter().check_unknowns()
