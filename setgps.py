import csv
import os
import platform

def main():
    CSV_FILE = "C:\\Users\\chris\\Downloads\\List of Stinehour sites - Sites.csv"
    PICTURE_DIRECTORY = "C:\\Users\\chris\\Pictures\\Stinehour Sites\\"
    if platform.system() == 'Linux':
        CSV_FILE = "/home/ck/Downloads/List of Stinehour sites - Sites.csv"
        PICTURE_DIRECTORY = "/home/ck/Pictures/Stinehour sites/"
    with open(CSV_FILE, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not row["Filename"]:
                print("Skipping row with no filename.")
                continue
            full_path = os.path.join(PICTURE_DIRECTORY, row["Filename"])
            latitude = row["Latitude"]
            longitude = row["Longitude"]
            if not latitude and not longitude:
                print(f"Skipping {full_path} due to missing GPS data.")
                continue
            # Case doesn't matter in Windows
            found = False
            for ext in ['.jpg', '.jpeg', '.png', '']:
                if os.path.exists(full_path + ext):
                    found = True
                    command = f'exiftool -GPSLatitude*="{latitude}" -GPSLongitude*="{longitude}" "{full_path + ext}"'
                    print(command)
                    os.system(command)
            if not found:
                print(f"File not found: {full_path}")

if __name__ == "__main__":
    main()
