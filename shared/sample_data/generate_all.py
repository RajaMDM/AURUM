"""
AURUM Sample Data Generator — v2.0
Produces deliberately dirty data across all 7 MDM domains.

Geographic data uses LINKED pairs — Dubai is always paired with a UAE
variant, London with a UK variant. Format variation (UAE/AE/United Arab
Emirates) is intentional dirt; geographic mismatch (Dubai/UK) would be
data corruption, not realistic dirt.

Each domain has 300–600 records. Total ~3,000 rows across 7 files.
"""
import csv
import random
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

random.seed(42)

# ---------------------------------------------------------------------------
# Shared name pools — with intentional duplicates / transliterations
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James", "James", "Jim", "Jamie",
    "Sara", "Sarah", "Sara",
    "Mohammed", "Mohamed", "Mohammad", "Mohamad",
    "Priya", "Priya", "Priyanka",
    "Chen", "Zhang", "Chan",
    "Fatima", "Fatimah", "Fatemah",
    "David", "Dave", "Dawood",
    "Anjali", "Anjalee",
    "Ravi", "Ravindra",
    "Hassan", "Hasan",
    "Nadia", "Nadya",
    "Oliver", "Ollie",
    "Sophie", "Sophia", "Sofia",
    "Tariq", "Tarek",
    "Meera", "Mira",
    "Khalid", "Khaled",
    "Emma", "Em",
    "Lucas", "Luca",
    "Aisha", "Ayesha",
]

LAST_NAMES = [
    "Smith", "Smith", "Smyth",
    "Johnson", "Johnston", "Johnstone",
    "Al-Rashid", "Al Rashid", "AlRashid",
    "Sharma", "Sharma",
    "Wang", "Wong",
    "Patel", "Patell",
    "Khan", "Khan",
    "Ali", "Aly",
    "Brown", "Browne",
    "Thomas", "Thomson",
    "Mitchell", "Mitchel",
    "Al-Farsi", "Al Farsi", "Alfarsi",
    "Gupta", "Guptha",
    "Singh", "Sing",
    "Martinez", "Martínez",
    "Ivanova", "Ivanov",
    "Nakamura", "Nakamara",
]

# ---------------------------------------------------------------------------
# Expanded globally-diverse CITY_COUNTRY_PAIRS (format variation only)
# ---------------------------------------------------------------------------
CITY_COUNTRY_PAIRS = [
    # UAE
    ("Dubai",                "UAE"),
    ("Dubai",                "AE"),
    ("Dubai",                "United Arab Emirates"),
    ("dubai",                "UAE"),
    ("DUBAI",                "AE"),
    ("Abu Dhabi",            "UAE"),
    ("Abu Dhabi",            "AE"),
    ("Abu Dhabi",            "United Arab Emirates"),
    ("abu dhabi",            "UAE"),
    ("Sharjah",              "UAE"),
    ("Sharjah",              "AE"),
    ("sharjah",              "UAE"),
    ("Ajman",                "UAE"),
    ("Ajman",                "AE"),
    ("Ras Al Khaimah",       "UAE"),
    ("RAK",                  "UAE"),
    # UK
    ("London",               "UK"),
    ("London",               "GB"),
    ("London",               "United Kingdom"),
    ("london",               "UK"),
    ("LONDON",               "GB"),
    ("Manchester",           "UK"),
    ("Manchester",           "GB"),
    ("manchester",           "UK"),
    ("Birmingham",           "UK"),
    ("Birmingham",           "GB"),
    ("Edinburgh",            "UK"),
    ("Edinburgh",            "GB"),
    # USA
    ("New York",             "US"),
    ("New York",             "USA"),
    ("New York City",        "US"),
    ("New York",             "United States"),
    ("NYC",                  "USA"),
    ("Houston",              "US"),
    ("Houston",              "USA"),
    ("Chicago",              "US"),
    ("Chicago",              "USA"),
    ("Los Angeles",          "US"),
    ("LA",                   "USA"),
    ("San Francisco",        "US"),
    ("SF",                   "USA"),
    # India
    ("Mumbai",               "India"),
    ("Mumbai",               "IN"),
    ("Bombay",               "India"),
    ("mumbai",               "India"),
    ("Delhi",                "India"),
    ("Delhi",                "IN"),
    ("New Delhi",            "India"),
    ("Bangalore",            "India"),
    ("Bangalore",            "IN"),
    ("Bengaluru",            "India"),
    ("Hyderabad",            "India"),
    ("Hyderabad",            "IN"),
    ("Chennai",              "India"),
    ("Chennai",              "IN"),
    # Saudi Arabia
    ("Riyadh",               "SA"),
    ("Riyadh",               "Saudi Arabia"),
    ("riyadh",               "SA"),
    ("Jeddah",               "SA"),
    ("Jeddah",               "Saudi Arabia"),
    ("Dammam",               "SA"),
    # Europe
    ("Paris",                "FR"),
    ("Paris",                "France"),
    ("paris",                "FR"),
    ("Berlin",               "DE"),
    ("Berlin",               "Germany"),
    ("berlin",               "DE"),
    ("Amsterdam",            "NL"),
    ("Amsterdam",            "Netherlands"),
    ("Zurich",               "CH"),
    ("Zurich",               "Switzerland"),
    ("zürich",               "CH"),
    ("Madrid",               "ES"),
    ("Madrid",               "Spain"),
    ("Milan",                "IT"),
    ("Milan",                "Italy"),
    ("Milano",               "IT"),
    # APAC
    ("Singapore",            "SG"),
    ("Singapore",            "Singapore"),
    ("singapore",            "SG"),
    ("Hong Kong",            "HK"),
    ("Hong Kong",            "China"),
    ("Hongkong",             "HK"),
    ("Sydney",               "AU"),
    ("Sydney",               "Australia"),
    ("sydney",               "AU"),
    ("Tokyo",                "JP"),
    ("Tokyo",                "Japan"),
    # Africa / Other
    ("Nairobi",              "KE"),
    ("Nairobi",              "Kenya"),
    ("Lagos",                "NG"),
    ("Lagos",                "Nigeria"),
    ("Cairo",                "EG"),
    ("Cairo",                "Egypt"),
    ("cairo",                "EG"),
]

CATEGORIES   = ["Electronics", "ELECTRONICS", "electronics", "Apparel", "apparel",
                 "APPAREL", "Food & Bev", "F&B", "Furniture", "FURNITURE",
                 "Automotive", "automotive", "Healthcare", "FMCG"]
UOM          = ["EA", "Each", "each", "Pc", "pc", "PCS", "KG", "kg", "Kg", "Unit", "UNIT"]
LIFECYCLES   = ["Active", "active", "ACTIVE", "In Use", "in_use", "IN_USE",
                "Maintenance", "MAINTENANCE", "Retired", "retired", "RETIRED",
                "Decommissioned", "decommissioned"]
PAY_TERMS    = ["Net30", "NET30", "Net 30", "30 days", "Net60", "NET60",
                "Net 60", "60 days", "Immediate", "COD", "15 days"]
CURRENCIES   = ["USD", "AED", "GBP", "EUR", "INR", "SAR", "SGD", "AUD"]
DEPARTMENTS  = ["Finance", "finance", "FINANCE", "Technology", "IT", "Information Technology",
                "Sales", "SALES", "sales", "Marketing", "marketing", "HR",
                "Human Resources", "Human resources", "Operations", "OPS",
                "Supply Chain", "Supply chain", "SUPPLY CHAIN", "Legal", "LEGAL",
                "Risk", "Compliance", "COMPLIANCE"]
JOB_TITLE_VARIANTS = {
    "Senior": ["Senior", "Sr", "Sr.", "SNR"],
    "Manager": ["Manager", "Mgr", "MGR"],
    "Director": ["Director", "Dir", "DIR"],
    "Analyst": ["Analyst", "Anlst", "ANALYST"],
    "Engineer": ["Engineer", "Engr", "Eng"],
}
STATUS_VARIANTS = ["Active", "active", "ACTIVE", "Inactive", "inactive",
                   "INACTIVE", "Employed", "employed", "Terminated"]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def dirty_phone_uae() -> str:
    base = f"+971-5{random.randint(0,9)}-{random.randint(1000000,9999999)}"
    return random.choice([
        base,
        base.replace("-", ""),
        base.replace("+971", "00971"),
        base[4:],
        f"05{random.randint(10000000,99999999)}",
    ])


def dirty_phone_uk() -> str:
    base = f"+44-7{random.randint(100,999)}-{random.randint(100000,999999)}"
    return random.choice([
        base,
        base.replace("-", ""),
        base.replace("+44", "0044"),
        f"07{random.randint(100,999)}{random.randint(100000,999999)}",
    ])


def dirty_phone_us() -> str:
    base = f"+1-{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
    return random.choice([
        base,
        base.replace("-", ""),
        base.replace("+1-", ""),
        f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
    ])


def dirty_phone() -> str:
    return random.choice([dirty_phone_uae, dirty_phone_uk, dirty_phone_us])()


def dirty_name(name: str) -> str:
    variants = [name, name.lower(), name.upper(), name + " ", " " + name]
    return random.choice(variants)


def dirty_date(year_start=1970, year_end=2000) -> str:
    y = random.randint(year_start, year_end)
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    formats = [
        f"{y}-{m:02d}-{d:02d}",
        f"{d:02d}/{m:02d}/{y}",
        f"{m:02d}-{d:02d}-{y}",
        f"{d:02d}-{m:02d}-{y}",
        f"{d} {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m-1]} {y}",
    ]
    return random.choice(formats)


def maybe_null(value: str, null_rate: float = 0.12) -> str:
    if random.random() < null_rate:
        return ""
    return value


def dirty_email(first: str, last: str, domain: str = "meridian.com") -> str:
    fn = first.strip().lower().replace(" ", "")
    ln = last.strip().lower().replace(" ", "")
    variants = [
        f"{fn}.{ln}@{domain}",
        f"{fn}{ln}@{domain}",
        f"{fn}.{ln}@{domain.upper()}",
        f"{fn[0]}{ln}@{domain}",
        f"{fn}@{domain}",
        f"{fn}.{ln}@{domain.replace('.com','.org')}",
        "",
    ]
    return random.choice(variants)


def make_lei(malform: bool = False) -> str:
    """Simulate a 20-char LEI code (ISO 17442)."""
    prefix = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=18))
    suffix = f"{random.randint(10,99)}"
    lei = prefix + suffix
    if malform:
        bad = [lei[:17], lei + "X", lei.replace(lei[5], ""), "N/A", "PENDING", ""]
        return random.choice(bad)
    return lei


# ---------------------------------------------------------------------------
# 1. CUSTOMERS  (600 rows)
# ---------------------------------------------------------------------------
def generate_customers(n: int = 600) -> None:
    path = OUTPUT_DIR / "customers_dirty.csv"
    sources = ["CRM", "ERP", "ECOMM", "LOYALTY", "PORTAL"]
    customer_types = ["B2C", "B2B", "VIP", "Corporate", "Retail", "Wholesale"]
    loyalty_tiers = ["Gold", "Silver", "Bronze", "Platinum", "None", "GOLD",
                     "silver", "PLATINUM", "", "N/A"]

    # Build ~80 "real" identities to create duplicate clusters
    identities = [
        (random.choice(FIRST_NAMES), random.choice(LAST_NAMES), random.choice(CITY_COUNTRY_PAIRS))
        for _ in range(80)
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "first_name", "last_name",
                         "email", "phone", "city", "country", "dob",
                         "customer_type", "loyalty_tier"])
        for i in range(1, n + 1):
            base_id = (i - 1) % len(identities)
            fn, ln, (city, country) = identities[base_id]
            src = random.choice(sources)
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                dirty_name(fn),
                dirty_name(ln),
                maybe_null(dirty_email(fn, ln), null_rate=0.08),
                maybe_null(dirty_phone(), null_rate=0.10),
                city,
                country,
                maybe_null(dirty_date(1965, 2000), null_rate=0.22),
                random.choice(customer_types),
                maybe_null(random.choice(loyalty_tiers), null_rate=0.05),
            ])
    print(f"  customers_dirty.csv     ({n} rows)")


# ---------------------------------------------------------------------------
# 2. PRODUCTS  (500 rows)
# ---------------------------------------------------------------------------
def generate_products(n: int = 500) -> None:
    path = OUTPUT_DIR / "products_dirty.csv"
    sources = ["PIM", "ERP", "ECOMM", "WMS", "MARKETPLACE"]
    brands = ["MeridianCorp", "MERIDIANCORP", "Meridian Corp", "meridian corp",
              "Verdant Apparel", "verdant", "VERDANT", "Verdant",
              "NorthBrew", "NORTHBREW", "North Brew",
              "AlphaGear", "ALPHAGEAR", "Alpha Gear",
              "ZenFit", "zenfit", "ZENFIT",
              "PeakTech", "Peak Tech", "PEAKTECH"]
    product_names = [
        ("Wireless Headphones",    "wireless headphones",    "WIRELESS HEADPHONES",    "Wireless Hdpn"),
        ("Running Shoes",          "running shoes",          "Running shoes",           "Run Shoes"),
        ("Coffee Blend A",         "coffee blend a",         "COFFEE BLEND A",          "Coffee-A"),
        ("Laptop Stand",           "laptop stand",           "LAPTOP STAND",            "Laptp Stand"),
        ("Yoga Mat",               "yoga mat",               "YOGA MAT",                "Yog Mat"),
        ("Office Chair",           "office chair",           "OFFICE CHAIR",            "Off Chair"),
        ("Bluetooth Speaker",      "bluetooth speaker",      "BT Speaker",              "BT Spkr"),
        ("Stainless Water Bottle", "stainless water bottle", "Stainless Wtrbottle",     "SS WtrBottle"),
        ("LED Desk Lamp",          "led desk lamp",          "LED lamp",                "Desk Lamp LED"),
        ("Protein Powder 1kg",     "protein powder 1 kg",    "Protein Powder",          "Prot Pwdr 1KG"),
        ("USB-C Hub 7-Port",       "usb-c hub 7port",        "USB C Hub",               "USBC Hub"),
        ("Smart Watch Gen3",       "smart watch gen 3",      "SmartWatch G3",           "SW-Gen3"),
        ("Winter Jacket M",        "winter jacket m",        "Winter Jacket (M)",       "WtrJkt-M"),
        ("Face Moisturizer 50ml",  "face moisturiser 50ml",  "Face Cream 50ml",         "FaceMoist50"),
    ]
    statuses = ["Active", "active", "ACTIVE", "Inactive", "Discontinued",
                "discontinued", "Draft", "DRAFT", "Published"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "sku", "name", "brand",
                         "category", "uom", "barcode", "price", "currency", "status"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            sku_base = f"SKU-{i:04d}"
            sku = random.choice([
                sku_base,
                sku_base.lower(),
                sku_base.replace("-", "_"),
                sku_base.replace("-", ""),
                f" {sku_base}",
                f"{sku_base} ",
            ])
            name_group = random.choice(product_names)
            price = round(random.uniform(5, 2500), 2)
            price_str = random.choice([
                str(price),
                f"{price:.0f}",
                f"${price:.2f}",
                f"{price:.2f} AED",
            ])
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                sku,
                random.choice(name_group),
                random.choice(brands),
                random.choice(CATEGORIES),
                random.choice(UOM),
                maybe_null(f"69{random.randint(10000000000,99999999999)}", null_rate=0.18),
                price_str,
                random.choice(CURRENCIES),
                random.choice(statuses),
            ])
    print(f"  products_dirty.csv      ({n} rows)")


# ---------------------------------------------------------------------------
# 3. VENDORS  (500 rows)
# ---------------------------------------------------------------------------
def generate_vendors(n: int = 500) -> None:
    path = OUTPUT_DIR / "vendors_dirty.csv"
    sources = ["ERP", "PROCUREMENT", "AP", "SUPPLIER_PORTAL"]

    vendor_bases = [
        ("Al Futtaim Group LLC",         "Al Futtaim",        "AE"),
        ("Majid Al Futtaim Properties",  "MAF Properties",    "AE"),
        ("Emaar Properties PJSC",        "Emaar",             "AE"),
        ("Noon.com FZCO",                "Noon",              "AE"),
        ("Carrefour UAE LLC",            "Carrefour",         "AE"),
        ("DEWA",                         "Dubai Electricity", "AE"),
        ("Emirates NBD",                 "ENBD",              "AE"),
        ("Lulu Hypermarket LLC",         "LuluHyper",         "AE"),
        ("Saudi Aramco",                 "Aramco",            "SA"),
        ("Saudi Basic Industries Corp",  "SABIC",             "SA"),
        ("stc (Saudi Telecom)",          "STC",               "SA"),
        ("Almarai Company",              "Almarai",           "SA"),
        ("National Commercial Bank",     "NCB",               "SA"),
        ("Tata Consultancy Services",    "TCS",               "IN"),
        ("Infosys Ltd",                  "Infosys",           "IN"),
        ("Wipro Limited",                "Wipro",             "IN"),
        ("Reliance Industries",          "Reliance",          "IN"),
        ("HDFC Bank",                    "HDFC",              "IN"),
        ("Siemens AG",                   "Siemens",           "DE"),
        ("SAP SE",                       "SAP",               "DE"),
        ("BASF SE",                      "BASF",              "DE"),
        ("Volkswagen AG",                "VW",                "DE"),
        ("Unilever PLC",                 "Unilever",          "GB"),
        ("HSBC Holdings plc",            "HSBC",              "GB"),
        ("BP PLC",                       "BP",                "GB"),
        ("Shell plc",                    "Shell",             "GB"),
        ("Barclays PLC",                 "Barclays",          "GB"),
        ("Amazon.com Inc",               "Amazon",            "US"),
        ("Microsoft Corporation",        "Microsoft",         "US"),
        ("Oracle Corporation",           "Oracle",            "US"),
        ("Salesforce Inc",               "Salesforce",        "US"),
        ("IBM Corporation",              "IBM",               "US"),
        ("Deloitte Consulting LLP",      "Deloitte",          "US"),
        ("KPMG International",           "KPMG",              "GB"),
        ("PricewaterhouseCoopers",       "PwC",               "GB"),
        ("Accenture PLC",                "Accenture",         "IE"),
        ("Ericsson AB",                  "Ericsson",          "SE"),
        ("Nokia Corporation",            "Nokia",             "FI"),
        ("NTT Data Corporation",         "NTT Data",          "JP"),
        ("Singtel",                      "Singtel",           "SG"),
    ]

    vendor_categories = ["IT Services", "Logistics", "Facilities", "Marketing",
                         "Manufacturing", "Consulting", "Raw Materials", "Software",
                         "Professional Services", "Telecoms", "Finance", "Energy"]
    tax_id_formats = {
        "AE": lambda: f"TRN{random.randint(100000000000000, 999999999999999)}",
        "SA": lambda: f"{random.randint(100000000,999999999)}",
        "IN": lambda: f"GSTIN{random.randint(10,29)}{random.choice(['AABC','XYZD','PQRS'])}{random.randint(10000,99999)}",
        "DE": lambda: f"DE{random.randint(100000000,999999999)}",
        "GB": lambda: f"GB{random.randint(100000000,999999999)}",
        "US": lambda: f"{random.randint(10,99)}-{random.randint(1000000,9999999)}",
    }
    city_for_country = {
        "AE": ["Dubai", "Abu Dhabi", "Sharjah"],
        "SA": ["Riyadh", "Jeddah", "Dammam"],
        "IN": ["Mumbai", "Bangalore", "Delhi"],
        "DE": ["Berlin", "Munich", "Frankfurt"],
        "GB": ["London", "Manchester", "Birmingham"],
        "US": ["New York", "Houston", "Chicago"],
        "IE": ["Dublin"],
        "SE": ["Stockholm"],
        "FI": ["Helsinki"],
        "JP": ["Tokyo"],
        "SG": ["Singapore"],
    }

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "vendor_id", "legal_name",
                         "trading_name", "tax_id", "country", "city",
                         "contact_email", "payment_terms", "category", "status"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            legal, trading, country_code = random.choice(vendor_bases)
            # Dirty the legal/trading names
            legal_dirty = random.choice([
                legal,
                legal.upper(),
                legal.lower(),
                legal.replace(" LLC", "").replace(" Ltd", "").replace(" PLC", ""),
                f" {legal}",
                legal + " ",
            ])
            trading_dirty = random.choice([
                trading,
                trading.upper(),
                trading.lower(),
                trading + " Group",
                f"{trading} Co.",
            ])
            # Country code dirty variants
            country_dirty = random.choice([
                country_code,
                country_code.lower(),
                {"AE": "UAE", "SA": "Saudi Arabia", "IN": "India",
                 "DE": "Germany", "GB": "UK", "US": "USA"}.get(country_code, country_code),
            ])
            tax_fmt = tax_id_formats.get(country_code, lambda: f"TAX{random.randint(100000,999999)}")
            tax_id = maybe_null(tax_fmt(), null_rate=0.15)
            if tax_id and random.random() < 0.12:
                # Dirty the tax ID slightly
                tax_id = tax_id[:-2] + "XX"

            cities = city_for_country.get(country_code, ["Unknown"])
            city = random.choice(cities)
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            email = maybe_null(dirty_email(fn, ln, f"{trading.lower().replace(' ','')}.com"), null_rate=0.10)

            vendor_id_variants = [
                f"VND-{i:05d}",
                f"V{i:05d}",
                f"VENDOR_{i:04d}",
                f"sup-{i:04d}",
            ]
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                random.choice(vendor_id_variants),
                legal_dirty,
                trading_dirty,
                tax_id,
                country_dirty,
                city,
                email,
                random.choice(PAY_TERMS),
                random.choice(vendor_categories),
                random.choice(["Active", "active", "ACTIVE", "Inactive", "Suspended", "On Hold"]),
            ])
    print(f"  vendors_dirty.csv       ({n} rows)")


# ---------------------------------------------------------------------------
# 4. ASSETS  (400 rows)
# ---------------------------------------------------------------------------
def generate_assets(n: int = 400) -> None:
    path = OUTPUT_DIR / "assets_dirty.csv"
    sources = ["CMDB", "ERP", "FM", "ITSM"]
    asset_descs = [
        ("Laptop",              "Laptop",           "LAPTOP",         "HP Laptop",       "Dell Laptop"),
        ("HVAC Unit",           "hvac unit",        "HVAC",           "Air Conditioning","Air Con Unit"),
        ("POS Terminal",        "pos terminal",     "POS",            "Point of Sale",   "POS Terminal"),
        ("Server Rack",         "server rack",      "SERVER RACK",    "Rack Server",     "Svr Rack"),
        ("Security Camera",     "security camera",  "CCTV",           "IP Camera",       "Sec Cam"),
        ("Forklift",            "forklift",         "FORKLIFT",       "Fork Lift",       "FL Unit"),
        ("Generator",           "generator",        "GENERATOR",      "Diesel Generator","Gen Set"),
        ("UPS Unit",            "ups unit",         "UPS",            "Uninterruptible", "Battery UPS"),
        ("Printer",             "printer",          "PRINTER",        "Laser Printer",   "MFP"),
        ("Tablet",              "tablet",           "TABLET",         "iPad",            "Android Tab"),
        ("Mobile Phone",        "mobile phone",     "MOBILE",         "Smartphone",      "Cell Phone"),
        ("Network Switch",      "network switch",   "SWITCH",         "L2 Switch",       "Ethernet Switch"),
        ("Projector",           "projector",        "PROJECTOR",      "LCD Projector",   "Beam Projector"),
        ("Fire Suppression",    "fire suppression", "FIRE SUPP",      "FM200 System",    "Fire Sys"),
    ]
    asset_cats = ["IT", "it", "Facilities", "FACILITIES", "Operations",
                  "operations", "Security", "SECURITY", "Mechanical", "MECHANICAL"]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "asset_tag", "serial_number",
                         "description", "category", "lifecycle_state",
                         "location_id", "assigned_to", "purchase_date", "value"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            tag = f"AST-{i:04d}"
            tag_dirty = random.choice([
                tag, tag.lower(), tag.replace("-", ""), f"{tag} ", f"AST{i:04d}", f"ast-{i:04d}",
            ])
            desc_group = random.choice(asset_descs)
            serial = f"SN{random.randint(1000000000, 9999999999)}"
            serial_dirty = maybe_null(serial, null_rate=0.16)
            if serial_dirty and random.random() < 0.08:
                serial_dirty = serial_dirty + "-" + random.choice(["A", "B", "R", ""])
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            assigned = maybe_null(f"{fn} {ln}", null_rate=0.20)
            loc = maybe_null(f"LOC-{random.randint(1,50):03d}", null_rate=0.18)
            value = round(random.uniform(100, 50000), 2)
            value_str = random.choice([str(value), f"${value:.2f}", f"{value:.0f}", f"{value:.2f} USD"])
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                tag_dirty,
                serial_dirty,
                random.choice(desc_group),
                random.choice(asset_cats),
                random.choice(LIFECYCLES),
                loc,
                assigned,
                maybe_null(dirty_date(2015, 2024), null_rate=0.10),
                value_str,
            ])
    print(f"  assets_dirty.csv        ({n} rows)")


# ---------------------------------------------------------------------------
# 5. LOCATIONS  (300 rows)
# ---------------------------------------------------------------------------
def generate_locations(n: int = 300) -> None:
    path = OUTPUT_DIR / "locations_dirty.csv"
    sources = ["ERP", "WMS", "YEXT", "CRM", "FM"]
    loc_names = [
        ("Dubai Mall Store",         "dubai mall store",  "DUBAI MALL STORE",  "DubaiMall",     "Dubai Mall"),
        ("Marina Walk Store",        "marina walk store", "MARINA WALK",       "MarinWalk",     "Marina Walk Store"),
        ("Abu Dhabi HQ",             "abu dhabi hq",      "ABU DHABI HQ",      "AD HQ",         "AbuDhabi HQ"),
        ("Riyadh Warehouse",         "riyadh warehouse",  "RIYADH WH",         "RUH Warehouse", "Riyadh WH"),
        ("London Office",            "london office",     "LONDON OFFICE",     "LON Off",       "London Off"),
        ("Mumbai DC",                "mumbai dc",         "MUMBAI DC",         "BOM DC",        "Mumbai Dist Ctr"),
        ("Singapore Hub",            "singapore hub",     "SINGAPORE HUB",     "SG Hub",        "Spore Hub"),
        ("New York Showroom",        "new york showroom", "NEW YORK SHOWROOM", "NYC Show",      "NY Showroom"),
        ("Berlin Distribution",      "berlin distrib",    "BERLIN DISTR",      "BER Dist",      "Berlin Dist Ctr"),
        ("Manchester Depot",         "manchester depot",  "MANCHESTER DEPOT",  "MCR Depot",     "Manch Depot"),
        ("Paris Boutique",           "paris boutique",    "PARIS BOUTIQUE",    "PAR Boutique",  "Paris Store"),
        ("Cairo Office",             "cairo office",      "CAIRO OFFICE",      "CAI Off",       "Cairo Off"),
    ]
    loc_types = ["Store", "store", "STORE", "retail", "Retail",
                 "Warehouse", "warehouse", "WH", "WAREHOUSE",
                 "Office", "office", "OFFICE", "HQ",
                 "DC", "Distribution Center", "Distribution Centre", "DIST CTR",
                 "Hub", "HUB", "Depot", "DEPOT"]
    timezones = ["Asia/Dubai", "Asia/Riyadh", "Europe/London", "America/New_York",
                 "Asia/Kolkata", "Asia/Singapore", "Europe/Paris", "Europe/Berlin",
                 "Australia/Sydney", "Asia/Tokyo", "Africa/Nairobi"]

    postal_codes = {
        "UAE": ["", ""],                    # UAE has no postal codes
        "AE": ["", ""],
        "UK": ["EC1A 1BB", "W1A 0AX", "SW1A 2AA", "M1 1AE"],
        "GB": ["EC1A 1BB", "W1A 0AX", "SW1A 2AA"],
        "US": ["10001", "10002", "90001", "60601", "77001"],
        "USA": ["10001", "90001", "60601"],
        "India": ["400001", "110001", "560001", "500001"],
        "IN": ["400001", "110001", "560001"],
        "SA": ["11564", "21462", "31952"],
        "DE": ["10115", "80331", "60311"],
        "Germany": ["10115", "80331", "60311"],
        "FR": ["75001", "75008", "69001"],
        "France": ["75001", "75008"],
        "SG": ["018989", "049315", "238880"],
    }

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "location_code", "name",
                         "type", "address_line1", "city", "country",
                         "postal_code", "lat", "lon", "parent_id", "timezone"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            code = f"LOC-{i:03d}"
            code_dirty = random.choice([code, code.lower(), code.replace("-", "_"), f" {code}", f"LOC{i:03d}"])
            city, country = random.choice(CITY_COUNTRY_PAIRS)
            name_group = random.choice(loc_names)
            postal = maybe_null(
                random.choice(postal_codes.get(country, [""])),
                null_rate=0.20
            )
            # Lat/lon — occasionally null or zero (Null Island detect test)
            if random.random() < 0.12:
                lat, lon = "", ""
            elif random.random() < 0.05:
                lat, lon = "0.0", "0.0"  # Null Island
            else:
                lat = str(round(random.uniform(-90, 90), 6))
                lon = str(round(random.uniform(-180, 180), 6))
            address_variants = [
                f"{random.randint(1,200)} Main Street",
                f"{random.randint(1,200)} Main St",
                f"{random.randint(1,200)} MAIN ST",
                f"Plot {random.randint(1,999)}, Industrial Area",
                f"Block {random.choice(['A','B','C'])}, Floor {random.randint(1,30)}",
                "",
            ]
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                code_dirty,
                random.choice(name_group),
                random.choice(loc_types),
                random.choice(address_variants),
                city,
                country,
                postal,
                lat,
                lon,
                maybe_null(f"LOC-{random.randint(1,10):03d}", null_rate=0.35),
                random.choice(timezones),
            ])
    print(f"  locations_dirty.csv     ({n} rows)")


# ---------------------------------------------------------------------------
# 6. EMPLOYEES  (400 rows)
# ---------------------------------------------------------------------------
def generate_employees(n: int = 400) -> None:
    path = OUTPUT_DIR / "employees_dirty.csv"
    sources = ["HRMS", "AD", "PAYROLL", "ERP"]

    roles = [
        ("Senior Data Engineer",   "Sr Data Engineer",    "SNR Data Eng",        "Senior Engr Data"),
        ("Data Analyst",           "data analyst",        "DATA ANALYST",        "Anlst Data"),
        ("Product Manager",        "product manager",     "Product Mgr",         "Prod Mgr"),
        ("HR Business Partner",    "HR Business Partner", "HRBP",                "HR BP"),
        ("Finance Manager",        "Finance Manager",     "Finance Mgr",         "Fin Manager"),
        ("Sales Director",         "Sales Director",      "Sales Dir",           "DIR Sales"),
        ("Software Engineer",      "software engineer",   "SW Engineer",         "Engr Software"),
        ("Marketing Analyst",      "marketing analyst",   "Mktg Analyst",        "Marketing Anlst"),
        ("Operations Manager",     "Operations Manager",  "Ops Mgr",             "Ops Manager"),
        ("Compliance Officer",     "compliance officer",  "Compliance Off",      "Compliance Ofcr"),
        ("Supply Chain Manager",   "Supply Chain Mgr",    "SC Manager",          "Sup Chain Mgr"),
        ("IT Support Specialist",  "IT Support",          "IT Support Spec",     "IT Spec"),
        ("Chief Financial Officer","CFO",                 "Chief Finance Ofcr",  "C.F.O"),
        ("Legal Counsel",          "Legal Counsel",       "legal counsel",       "Counsel Legal"),
    ]
    cost_centres = [f"CC-{n:04d}" for n in [1001, 1002, 1003, 2001, 2002, 3001, 3002, 4001, 5001, 5002]]
    emp_statuses = ["Active", "active", "ACTIVE", "Inactive", "inactive",
                    "INACTIVE", "Employed", "employed", "Terminated", "On Leave"]

    # Pre-generate manager IDs to reference
    manager_ids = [f"EMP-{i:05d}" for i in range(1, 51)]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "employee_id",
                         "first_name", "last_name", "email",
                         "department", "job_title", "manager_id",
                         "hire_date", "status", "location_id", "cost_centre"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            dept = random.choice(DEPARTMENTS)
            role_group = random.choice(roles)
            emp_id_variants = [
                f"EMP-{i:05d}",
                f"E{i:05d}",
                f"emp_{i:04d}",
                f"EMP{i:05d}",
            ]
            email_domain = "corp.meridian.com"
            email_formats = [
                f"{fn.lower()}.{ln.lower()}@{email_domain}",
                f"{fn.lower()}{ln.lower()}@{email_domain}",
                f"{fn[0].lower()}{ln.lower()}@{email_domain}",
                f"{fn.lower()}.{ln.lower()}@{email_domain.upper()}",
                "",
            ]
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                random.choice(emp_id_variants),
                dirty_name(fn),
                dirty_name(ln),
                maybe_null(random.choice(email_formats), null_rate=0.06),
                dirty_name(dept),
                random.choice(role_group),
                maybe_null(random.choice(manager_ids), null_rate=0.25),
                maybe_null(dirty_date(2010, 2024), null_rate=0.08),
                random.choice(emp_statuses),
                maybe_null(f"LOC-{random.randint(1,30):03d}", null_rate=0.15),
                maybe_null(random.choice(cost_centres), null_rate=0.12),
            ])
    print(f"  employees_dirty.csv     ({n} rows)")


# ---------------------------------------------------------------------------
# 7. COUNTERPARTIES  (300 rows)
# ---------------------------------------------------------------------------
def generate_counterparties(n: int = 300) -> None:
    path = OUTPUT_DIR / "counterparties_dirty.csv"
    sources = ["CRM", "ERP", "LEGAL", "COMPLIANCE", "TREASURY"]

    cp_bases = [
        ("Emirates Investment Authority",  "EIA",         "AE"),
        ("Abu Dhabi Investment Authority", "ADIA",        "AE"),
        ("Mubadala Investment Company",    "Mubadala",    "AE"),
        ("Investment Corp of Dubai",       "ICD",         "AE"),
        ("Public Investment Fund",         "PIF",         "SA"),
        ("Saudi Aramco Trading",           "Aramco Trdg", "SA"),
        ("SABIC Trading",                  "SABIC",       "SA"),
        ("Temasek Holdings",               "Temasek",     "SG"),
        ("GIC Private Limited",            "GIC",         "SG"),
        ("Norges Bank Investment Mgmt",    "NBIM",        "NO"),
        ("Qatar Investment Authority",     "QIA",         "QA"),
        ("Kuwait Investment Authority",    "KIA",         "KW"),
        ("Khazanah Nasional",              "Khazanah",    "MY"),
        ("BlackRock Inc",                  "BlackRock",   "US"),
        ("Vanguard Group",                 "Vanguard",    "US"),
        ("JPMorgan Chase",                 "JPM",         "US"),
        ("Goldman Sachs Group",            "Goldman",     "US"),
        ("Citigroup Inc",                  "Citi",        "US"),
        ("HSBC Holdings",                  "HSBC",        "GB"),
        ("Standard Chartered PLC",         "StanChart",   "GB"),
        ("Lloyds Banking Group",           "Lloyds",      "GB"),
        ("Deutsche Bank AG",               "DB",          "DE"),
        ("BNP Paribas SA",                 "BNP",         "FR"),
        ("Credit Suisse Group",            "CS",          "CH"),
        ("UBS Group AG",                   "UBS",         "CH"),
        ("Mitsubishi UFJ Financial",       "MUFG",        "JP"),
        ("Industrial & Commercial Bank",   "ICBC",        "CN"),
        ("Bank of China",                  "BoC",         "CN"),
        ("Reliance Capital",               "Rel Capital", "IN"),
        ("HDFC Ltd",                       "HDFC",        "IN"),
    ]

    roles = ["Customer", "Vendor", "Both", "Investor", "Partner",
             "customer", "vendor", "CUSTOMER", "VENDOR",
             "Counterparty", "counterparty"]
    jurisdictions = {
        "AE": ["UAE", "AE", "United Arab Emirates", "DIFC", "ADGM"],
        "SA": ["SA", "Saudi Arabia", "KSA"],
        "SG": ["SG", "Singapore", "SGP"],
        "US": ["US", "USA", "United States", "NY", "DE"],
        "GB": ["GB", "UK", "United Kingdom", "England"],
        "DE": ["DE", "Germany", "Deutschland"],
        "FR": ["FR", "France"],
        "CH": ["CH", "Switzerland", "CHE"],
        "JP": ["JP", "Japan"],
        "QA": ["QA", "Qatar"],
        "KW": ["KW", "Kuwait"],
        "NO": ["NO", "Norway"],
        "MY": ["MY", "Malaysia"],
        "CN": ["CN", "China", "PRC"],
        "IN": ["IN", "India", "IND"],
    }

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["source_id", "source_system", "counterparty_id",
                         "legal_name", "short_name", "lei_code",
                         "jurisdiction", "role", "contact_email",
                         "relationship_start", "status"])
        for i in range(1, n + 1):
            src = random.choice(sources)
            legal, short, country_code = random.choice(cp_bases)
            legal_dirty = random.choice([
                legal,
                legal.upper(),
                legal.lower(),
                legal.replace(" ", ""),
                legal + " Ltd",
                legal.replace("Group", "Grp").replace("Holdings", "Hldgs"),
                f" {legal}",
            ])
            short_dirty = random.choice([
                short, short.upper(), short.lower(),
                short + " Group", short.replace(" ", ""),
            ])
            jur_list = jurisdictions.get(country_code, [country_code])
            jur = random.choice(jur_list)
            # LEI — some valid, some malformed, some missing
            lei_roll = random.random()
            if lei_roll < 0.55:
                lei = make_lei(malform=False)
            elif lei_roll < 0.80:
                lei = make_lei(malform=True)
            else:
                lei = ""
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            cp_id_variants = [
                f"CP-{i:05d}",
                f"CTY-{i:04d}",
                f"cp_{i:04d}",
                f"CPTY{i:04d}",
            ]
            writer.writerow([
                f"{src}-{i:05d}",
                src,
                random.choice(cp_id_variants),
                legal_dirty,
                short_dirty,
                lei,
                jur,
                random.choice(roles),
                maybe_null(dirty_email(fn, ln, f"{short.lower().replace(' ','')}.com"), null_rate=0.12),
                maybe_null(dirty_date(2010, 2024), null_rate=0.10),
                random.choice(["Active", "active", "ACTIVE", "Inactive", "Suspended", "Review"]),
            ])
    print(f"  counterparties_dirty.csv ({n} rows)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("AURUM Sample Data Generator — v2.0")
    print("=" * 50)
    generate_customers(600)
    generate_products(500)
    generate_vendors(500)
    generate_assets(400)
    generate_locations(300)
    generate_employees(400)
    generate_counterparties(300)
    print("=" * 50)
    total = 600 + 500 + 500 + 400 + 300 + 400 + 300
    print(f"Total rows generated : {total:,}")
    print(f"Output directory     : {OUTPUT_DIR}")
    print()
    print("Domain summary:")
    print("  Customer       600 rows  →  customers_dirty.csv")
    print("  Product        500 rows  →  products_dirty.csv")
    print("  Vendor         500 rows  →  vendors_dirty.csv")
    print("  Asset          400 rows  →  assets_dirty.csv")
    print("  Location       300 rows  →  locations_dirty.csv")
    print("  Employee       400 rows  →  employees_dirty.csv")
    print("  Counterparty   300 rows  →  counterparties_dirty.csv")
