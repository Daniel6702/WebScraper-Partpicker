from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import re
import json


def estimate_psu_wattage(price):
    a = 400 / 1500
    b = 350 - a * 500
    wattage = a * price + b
    return max(300, min(1000, round(wattage)))

def extract_wattage(name):
    wattage_patterns = [
        r'(\d+) ?Watt',
        r'(\d+) ?W',
        r'(\d+) ?kW',  
    ]
    for pattern in wattage_patterns:
        match = re.search(pattern, name)
        if match:
            if 'kW' in pattern:
                return int(match.group(1)) * 1000
            return int(match.group(1))
    return None

def load_psu_data():
    psu_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        psu_urls += ProductURLFetcher.from_source(source, 'psu').get_product_urls()
    psu_data = []
    for url in tqdm(psu_urls, desc="Scraping Data", unit="url"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        wattage = extract_wattage(info['name'])
        if wattage is None:
            continue
        info['wattage'] = wattage
        psu_data.append(info)
    print("PSU Loading complete...")
    with open('MainData\psu_data.json', 'w', encoding='utf-8') as f:
        json.dump(psu_data, f, ensure_ascii=False, indent=4)

load_psu_data()