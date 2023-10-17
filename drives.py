from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import re
import json

def retrieve_drive_info(product_name):
    type = None
    capacity = None
    interface = None
    product_name = product_name.lower()
    if 'ssd' in product_name or 'nvme' in product_name or 'm.2' in product_name or 'pci' in product_name or 'solid state drive' in product_name:
        type = 'SSD'
    else:
        type = 'HDD'
    if 'nvme' in product_name or 'm.2' in product_name or 'pci' in product_name and 'sata' not in product_name and 'sas' not in product_name and '2.5' not in product_name and '3.5' not in product_name:
        interface = 'm.2'
    else:
        interface = 'sata'
    if 'portable' in product_name or 'ekstern' in product_name or 'external' in product_name:
        interface = 'usb'
    capacity_patterns = [
        r'(\d+(\.\d+)?)\s*(gib|gb)',
        r'(\d+(\.\d+)?)\s*(tb|terabyte)',
    ]
    for pattern in capacity_patterns:
        match = re.search(pattern, product_name)
        if match:
            capacity = float(match.group(1))
            unit = match.group(3)
            if unit in ['tb', 'terabyte']:
                capacity *= 1000
    return {'type': type, 'capacity': capacity, 'interface': interface}

def load_drive_data():
    drive_urls = []
    sources = ['proshop', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        drive_urls += ProductURLFetcher.from_source(source, 'drives').get_product_urls()
    drive_data = []
    for url in tqdm(drive_urls, desc="Scraping data", unit="case"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        specs = retrieve_drive_info(info['name'])
        if specs['capacity'] is None or specs['type'] is None or specs['interface'] is None:
            continue
        info.update(specs)
        drive_data.append(info)
    print("Case Loading complete...")
    with open('MainData\drive_data.json', 'w', encoding='utf-8') as f:
        json.dump(drive_data, f, ensure_ascii=False, indent=4)
    return drive_data

load_drive_data()