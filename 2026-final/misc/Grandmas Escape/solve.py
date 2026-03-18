import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


R = 6_371_000.0
base = Path(__file__).resolve().parent

towers = json.loads((base / "cell_towers.json").read_text())
signals = defaultdict(list)

with (base / "signals.csv").open(newline="") as f:
    for row in csv.DictReader(f):
        signals[row["mast"]].append(float(row["rssi"]))

median_rssi = {name: statistics.median(values) for name, values in signals.items()}
lat0 = sum(t["latitude"] for t in towers) / len(towers)
lon0 = sum(t["longitude"] for t in towers) / len(towers)
lat0_rad = math.radians(lat0)

points = {}
distances = {}
for tower in towers:
    name = tower["name"]
    points[name] = (
        math.radians(tower["longitude"] - lon0) * R * math.cos(lat0_rad),
        math.radians(tower["latitude"] - lat0) * R,
    )
    distances[name] = 10 ** ((-30.0 - median_rssi[name]) / 20.0)

ref = min(distances, key=distances.get)
x1, y1 = points[ref]
d1 = distances[ref]
s11 = s12 = s22 = t1 = t2 = 0.0

for name, di in distances.items():
    if name == ref:
        continue
    xi, yi = points[name]
    ax = 2.0 * (xi - x1)
    ay = 2.0 * (yi - y1)
    rhs = (xi * xi + yi * yi - di * di) - (x1 * x1 + y1 * y1 - d1 * d1)
    s11 += ax * ax
    s12 += ax * ay
    s22 += ay * ay
    t1 += ax * rhs
    t2 += ay * rhs

det = s11 * s22 - s12 * s12
x = (t1 * s22 - t2 * s12) / det
y = (s11 * t2 - s12 * t1) / det
lat = lat0 + math.degrees(y / R)
lon = lon0 + math.degrees(x / (R * math.cos(lat0_rad)))

print(lat)
print(lon)
