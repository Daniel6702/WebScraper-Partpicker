from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import re
import json

def extract_ram_info(product_name):
    # Regular expressions to extract information
    capacity_pattern = r'(\d+)\s?GB'
    mhz_pattern = r'(\d+)\s?Mhz'
    type_pattern = r'DDR[0-9]+'
    sticks_pattern = r'(\d+)\s?x\s(\d+)\s?GB'
    alt_mhz_pattern = r'DDR[0-9]+-(\d+)\s?'

    # Extract capacity
    capacity_match = re.search(capacity_pattern, product_name)
    capacity = int(capacity_match.group(1)) if capacity_match else None

    # Extract MHz using the standard pattern
    mhz_match = re.search(mhz_pattern, product_name, re.IGNORECASE)
    mhz = int(mhz_match.group(1)) if mhz_match else None

    # Extract MHz using the alternative pattern
    if not mhz:
        alt_mhz_match = re.search(alt_mhz_pattern, product_name, re.IGNORECASE)
        mhz = int(alt_mhz_match.group(1)) if alt_mhz_match else None

    # Extract RAM type (DDR3, DDR4, DDR5)
    type_match = re.search(type_pattern, product_name)
    ram_type = type_match.group() if type_match else None

    # Extract number of sticks and stick capacity
    sticks_match = re.search(sticks_pattern, product_name)
    num_sticks = int(sticks_match.group(1)) if sticks_match else 1
    stick_capacity = int(sticks_match.group(2)) if sticks_match else capacity

    return {
        'Capacity': capacity,
        'MHz': mhz,
        'Type': ram_type,
        'Number of Sticks': num_sticks,
        'Stick Capacity': stick_capacity
    }
    
def calculate_ram_performance(capacity, mhz, num_sticks):
    # Define weights for each factor (you can adjust these as needed)
    capacity_weight = 0.4
    mhz_weight = 0.4
    num_sticks_weight = 0.2

    # Initialize performance to 0
    performance = 0.0

    # Calculate performance if capacity and mhz are not None
    if capacity is not None and mhz is not None:
        # Normalize capacity to a scale of 0-1
        normalized_capacity = capacity / 32  # Assuming a maximum of 32GB
        # Normalize MHz to a scale of 0-1 (assuming a maximum of 6400)
        normalized_mhz = mhz / 6400
        # Normalize num_sticks to a scale of 0-1 (assuming a maximum of 4)
        normalized_num_sticks = num_sticks / 4

        # Calculate performance metric
        performance = (
            normalized_capacity * capacity_weight +
            normalized_mhz * mhz_weight +
            normalized_num_sticks * num_sticks_weight
        )

    return performance

def load_ram_data():
    ram_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        ram_urls += ProductURLFetcher.from_source(source, 'ram').get_product_urls()
    ram_data = []
    for url in tqdm(ram_urls, desc="Scraping Data", unit="url"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        ram_specs = extract_ram_info(info['name'])
        performance = calculate_ram_performance(ram_specs['Capacity'], ram_specs['MHz'], ram_specs['Number of Sticks'])
        info['performance'] = performance
        info.update(ram_specs)
        ram_data.append(info)
    print("RAM Loading complete...")
    with open('MainData\\ram_data.json', 'w', encoding='utf-8') as f:
        json.dump(ram_data, f, ensure_ascii=False, indent=4)

load_ram_data()