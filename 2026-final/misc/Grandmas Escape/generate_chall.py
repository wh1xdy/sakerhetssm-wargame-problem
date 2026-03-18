import math
import csv
import random
import json
import xml.etree.ElementTree as ET

def haversine(lat1, lon1, lat2, lon2, R=6.3781*10**6):
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c

    return distance

def parse_kml_coordinates(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    ns = {
        "kml": "http://www.opengis.net/kml/2.2"
    }

    results = []

    for placemark in root.findall(".//kml:Placemark", ns):
        name_elem = placemark.find("kml:name", ns)
        coord_elem = placemark.find(".//kml:Point/kml:coordinates", ns)

        if name_elem is None or coord_elem is None:
            continue

        name = name_elem.text.strip()
        coord_text = coord_elem.text.strip()

        lon, lat, alt = map(float, coord_text.split(","))

        results.append((name, lat, lon, alt))

    return results

def rssi_from_distance(distance):
    return -30 - 20 * math.log10(distance)

#{Svappavaara67.65_21.05}
def generate_log(mormor, masts, samples=10000, noise_std=0.6):
    rows = []

    for t in range(samples):
        timestamp = t 
        for mast in masts:
            name = mast.get("name", "")
            lat = mast.get("latitude", "")
            lon = mast.get("longitude", "")
            distance = haversine(mormor[0], mormor[1], lat, lon)
            true_rssi = rssi_from_distance(distance)

            noise = random.gauss(0, noise_std)

            if random.random() < 0.05:
                noise += random.choice([5, -5])

            measured_rssi = true_rssi + noise

            rows.append([timestamp, name, round(measured_rssi, 2)])

    return rows

if __name__ == "__main__":
    coords = parse_kml_coordinates("map.kml")
    mormor = None
    masts = []

    for name, lat, lon, alt in coords:
        #print(f"{name}: lat={lat}, lon={lon}, alt={alt}")
        if name == "Mormor":
            mormor = (lat, lon)
        else:
            masts.append({
                "name": name,
                "latitude": lat,
                "longitude": lon,
            })

    rows = generate_log(mormor, masts)

    with open("signals.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "mast", "rssi"])
        writer.writerows(rows)

    with open("cell_towers.json", "w") as f:
        json.dump(masts, f, indent=4)