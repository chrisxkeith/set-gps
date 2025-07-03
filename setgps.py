import csv
import sys
import os

def main():
    # CSV_FILE = "/c/Users/chris/Downloads//List of Stinehour sites - Sites.csv"
    CSV_FILE = "C:\\Users\\chris\\Downloads\\List of Stinehour sites - Sites.csv"
    # PICTURE_DIRECTORY = ""
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            print(row["Filename"])

if __name__ == "__main__":
    main()
