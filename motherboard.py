from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import json

def extract_motherboard_info(name):
    cpu_sockets = [
        "AM5",
        "LGA 1700",
        "LGA 1200",
        "LGA 1151",
        "LGA 2066",
        "AM4",
        "TR4",
        "sTRX4",
        "FM2+",
        "AM3+",
        "LGA 2011-v3",
        "LGA 1150",
        "LGA 1155",
        "LGA 775",
        "AM3",
        "FM1",
        "FM2",
        "G34",
        "LGA 1356",
        "LGA 2011",
        "LGA 1366",
        "LGA 771"
    ]
    ram_types = [
        "DDR4",
        "DDR3",
        "DDR5"
    ]
    chipsets = [
        "Z790",
        "H770",
        "B760",
        "Z690",
        "H670",
        "B660",
        "H610",
        "Z590",
        "B560",
        "H570",
        "Z490",
        "B460",
        "H410",
        "A620",
        "B650",
        "X670",
        "X670E",
        "X570",
        "B550",
        "A520",
        "X470",
        "B450",
        "A320",
    ]

    extracted_info = {}
    name_lower = name.lower()
    extracted_info["socket"] = next((socket for socket in cpu_sockets if socket.lower() in name_lower), None)
    extracted_info["chipset"] = next((chipset for chipset in chipsets if chipset.lower() in name_lower), None)
    extracted_info["ram_type"] = next((ram_type for ram_type in ram_types if ram_type.lower() in name_lower), None)
    if extracted_info["chipset"] == "Z790" or extracted_info["chipset"] == "B760" or extracted_info["chipset"] == "H770" or extracted_info["chipset"] == "Z690" or extracted_info["chipset"] == "B660" or extracted_info["chipset"] == "H670":
        extracted_info["socket"] = "LGA 1700"
    elif extracted_info["chipset"] == "Z590" or extracted_info["chipset"] == "B560" or extracted_info["chipset"] == "H570":
        extracted_info["socket"] = "LGA 1200"
    elif extracted_info["chipset"] == "x670" or extracted_info["chipset"] == "X670e" or extracted_info["chipset"] == "A5620" or extracted_info["chipset"] == "B650":
        extracted_info["socket"] = "AM5"
    if "ddr4" in name_lower and "ddr5" in name_lower:
        extracted_info["ram_type"] = "ddr4/ddr5"
    else:
        extracted_info["ram_type"] = next((ram_type for ram_type in ram_types if ram_type.lower() in name_lower), None)
    if extracted_info["ram_type"] is None:
        if extracted_info["socket"] == 'AM5':
            extracted_info["ram_type"] = "DDR5"
        elif extracted_info["socket"] == 'AM4' or extracted_info["socket"] == 'LGA 1200' or extracted_info["socket"] == 'LGA 1151' or extracted_info["socket"] == 'LGA 2066' or extracted_info["socket"] == 'LGA 2011-v3' or extracted_info["socket"] == 'LGA 1150' or extracted_info["socket"] == 'LGA 1155' or extracted_info["socket"] == 'LGA 775' or extracted_info["socket"] == 'AM3' or extracted_info["socket"] == 'FM1' or extracted_info["socket"] == 'FM2' or extracted_info["socket"] == 'G34' or extracted_info["socket"] == 'LGA 1356' or extracted_info["socket"] == 'LGA 2011' or extracted_info["socket"] == 'LGA 1366' or extracted_info["socket"] == 'LGA 771':
            extracted_info["ram_type"] = "DDR4"
        
    return extracted_info
    
def load_motherboard_data():
    motherboard_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        motherboard_urls += ProductURLFetcher.from_source(source, 'bundkort').get_product_urls()
    motherboard_data = []
    for url in tqdm(motherboard_urls, desc="Scraping Data", unit="url"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        specs = extract_motherboard_info(info['name'])
        if None in specs.values():
            continue
        info.update(specs)
        motherboard_data.append(info)
    print("Motherboard Loading complete...")
    with open('MainData\motherboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(motherboard_data, f, ensure_ascii=False, indent=4)
        
    return motherboard_data

load_motherboard_data()

