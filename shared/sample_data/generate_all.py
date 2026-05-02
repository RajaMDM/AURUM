"""
AURUM Sample Data Generator
Produces deliberately dirty data across all 7 domains.

Geographic data uses LINKED pairs — Dubai is always paired with a UAE
variant, London with a UK variant. Format variation (UAE/AE/United Arab
Emirates) is intentional dirt; geographic mismatch (Dubai/UK) would be
data corruption, not realistic dirt.
"""
import csv
import random
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

random.seed(42)

FIRST_NAMES = ["James","James","Jim","Jamie","Sara","Sarah","Sara","Mohammed","Mohamed","Priya","Priya","Chen","Zhang"]
LAST_NAMES  = ["Smith","Smith","Smyth","Johnson","Johnston","Al-Rashid","Al Rashid","Sharma","Sharma","Wang","Wong"]

# Linked geographic tuples — format variation only, never geographic mismatch
CITY_COUNTRY_PAIRS = [
    ("Dubai",         "UAE"),
    ("Dubai",         "AE"),
    ("Dubai",         "United Arab Emirates"),
    ("dubai",         "UAE"),
    ("DUBAI",         "AE"),
    ("Abu Dhabi",     "UAE"),
    ("Abu Dhabi",     "AE"),
    ("Sharjah",       "UAE"),
    ("Sharjah",       "AE"),
    ("London",        "UK"),
    ("London",        "GB"),
    ("London",        "United Kingdom"),
    ("london",        "UK"),
    ("New York",      "US"),
    ("New York",      "USA"),
    ("New York City", "US"),
    ("New York",      "United States"),
]

CATEGORIES  = ["Electronics","ELECTRONICS","electronics","Apparel","apparel","APPAREL","Food & Bev","F&B"]
UOM         = ["EA","Each","each","Pc","pc","PCS","KG","kg","Kg"]
LIFECYCLES  = ["Active","active","ACTIVE","In Use","in_use","Maintenance","MAINTENANCE","Retired","retired"]


def dirty_phone() -> str:
    base = f"+971-5{random.randint(0,9)}-{random.randint(1000000,9999999)}"
    return random.choice([base, base.replace("-",""), base.replace("+971","00971"), base[4:]])


def dirty_name(name: str) -> str:
    variants = [name, name.lower(), name.upper(), name.replace("a","@"), name + " "]
    return random.choice(variants)


def generate_customers(n: int = 80) -> None:
    path = OUTPUT_DIR / "customers_dirty.csv"
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id","source_system","first_name","last_name","email","phone","city","country","dob"])
        for i in range(1, n + 1):
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            city, country = random.choice(CITY_COUNTRY_PAIRS)
            email_variants = [
                f"{fn.lower()}.{ln.lower()}@meridian.com",
                f"{fn.lower()}{ln.lower()}@meridian.com",
                f"{fn.lower()}.{ln.lower()}@MERIDIAN.COM",
                "",
                f"{fn.lower()}@meridian.com",
            ]
            writer.writerow([
                f"CRM-{i:05d}",
                random.choice(["CRM","ERP","ECOMM","LOYALTY"]),
                dirty_name(fn),
                dirty_name(ln),
                random.choice(email_variants),
                dirty_phone() if random.random() > 0.1 else "",
                city,
                country,
                f"{random.randint(1970,2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}" if random.random() > 0.2 else "",
            ])
    print(f"  customers_dirty.csv  ({n} rows)")


def generate_products(n: int = 60) -> None:
    path = OUTPUT_DIR / "products_dirty.csv"
    brands = ["MeridianCorp","MERIDIANCORP","Meridian Corp","Verdant Apparel","verdant","NorthBrew","NORTHBREW"]
    names  = ["Wireless Headphones","wireless headphones","WIRELESS HEADPHONES",
               "Running Shoes","running shoes","Running shoes","Coffee Blend A","coffee blend a"]
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id","source_system","sku","name","brand","category","uom","barcode"])
        for i in range(1, n + 1):
            sku_base = f"SKU-{i:04d}"
            writer.writerow([
                f"PIM-{i:05d}",
                random.choice(["PIM","ERP","ECOMM","WMS"]),
                random.choice([sku_base, sku_base.lower(), sku_base.replace("-","_"), f" {sku_base}"]),
                random.choice(names),
                random.choice(brands),
                random.choice(CATEGORIES),
                random.choice(UOM),
                f"69{random.randint(10000000000,99999999999)}" if random.random() > 0.15 else "",
            ])
    print(f"  products_dirty.csv   ({n} rows)")


def generate_assets(n: int = 40) -> None:
    path = OUTPUT_DIR / "assets_dirty.csv"
    descs = ["Laptop","laptop","LAPTOP","HP Laptop","Dell Laptop",
             "HVAC Unit","hvac unit","HVAC unit","Air Conditioning Unit",
             "POS Terminal","pos terminal","POS terminal"]
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id","source_system","asset_tag","description","category","lifecycle_state","location_id"])
        for i in range(1, n + 1):
            tag = f"AST-{i:04d}"
            writer.writerow([
                f"CMDB-{i:05d}",
                random.choice(["CMDB","ERP","FM"]),
                random.choice([tag, tag.lower(), tag.replace("-",""), f"{tag} "]),
                random.choice(descs),
                random.choice(["IT","it","Facilities","FACILITIES","Operations"]),
                random.choice(LIFECYCLES),
                f"LOC-{random.randint(1,20):03d}" if random.random() > 0.2 else "",
            ])
    print(f"  assets_dirty.csv     ({n} rows)")


def generate_locations(n: int = 30) -> None:
    path = OUTPUT_DIR / "locations_dirty.csv"
    names = ["Dubai Mall Store","dubai mall store","Dubai Mall","Marina Walk","marina walk","Marina Walk Store"]
    types = ["Store","store","STORE","Warehouse","warehouse","Office","DC","Distribution Center"]
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id","source_system","location_code","name","type","city","country","parent_id"])
        for i in range(1, n + 1):
            code = f"LOC-{i:03d}"
            city, country = random.choice(CITY_COUNTRY_PAIRS)
            writer.writerow([
                f"ERP-{i:05d}",
                random.choice(["ERP","WMS","YEXT","CRM"]),
                random.choice([code, code.lower(), code.replace("-","_"), f" {code}"]),
                random.choice(names),
                random.choice(types),
                city,
                country,
                f"LOC-{random.randint(1,5):03d}" if random.random() > 0.4 else "",
            ])
    print(f"  locations_dirty.csv  ({n} rows)")


if __name__ == "__main__":
    print("AURUM Sample Data Generator")
    print("=" * 40)
    generate_customers()
    generate_products()
    generate_assets()
    generate_locations()
    print("=" * 40)
    print(f"Output: {OUTPUT_DIR}")
