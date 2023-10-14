import csv
from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import json
        
def get_names(csv_filepath):
    names = []
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            brand = row['Brand']
            model = row['Model']
            if brand in ['Nvidia', 'AMD']:
                names.append(model.replace('-', ' '))
    return names

def get_anti_keys(name):
    anti_keys = []
    name_upper = name.upper()
    if ("RTX" in name_upper or "GTX" in name_upper) and "TI" not in name_upper:
        anti_keys.append("ti")
    elif "RX" in name_upper and "XT" not in name_upper and "XTX" not in name_upper:
        anti_keys.extend(["xt", "xtx"])
    elif " HD " in name_upper:
        anti_keys.append("rx")
    return anti_keys

def get_keys(name):
    stopwords = ["Nvidia", "AMD", "Intel"]
    keys = [word.lower() for word in name.split() if word not in stopwords]
    keys = [key.replace("(", "").replace(")", "") for key in keys]
    keys = [" " + key + " " for key in keys]
    return keys

def create_id(name):
    name_hash = hash(name)
    random_id = abs(name_hash)
    return random_id

def get_performance(keys,anti_keys,csv_filepath):
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            model = row['Model'].upper()
            benchmark = row['Benchmark']
            if all(key.upper() in model for key in keys) and \
               not any(anti_key.upper() in model for anti_key in anti_keys):
                   return benchmark

def load_gpu_data():
    gpu_data = []
    names = get_names("BenchmarkData\GPU_UserBenchmarks.csv")
    for name in tqdm(names, desc="Loading GPU Specs", unit="spec"):
        keys = get_keys(name)
        anti_keys = get_anti_keys(name)
        id = create_id(name)
        benchmark = get_performance(keys, anti_keys, "BenchmarkData\GPU_UserBenchmarks.csv")
        data = {
            "name": name,
            "keys": keys,
            "anti_keys": anti_keys,
            "id": id,
            "performance": benchmark,
            "variants": []
        }
        gpu_data.append(data)
    gpu_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        gpu_urls += ProductURLFetcher.from_source(source, 'grafikkort').get_product_urls()
    for url in tqdm(gpu_urls, desc="Scraping Data", unit="url"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        if info['name'] is not None:
            name = info['name'].upper()
            for gpu in gpu_data:
                keys = gpu['keys']
                anti_keys = gpu['anti_keys']
                if all(key.upper() in name for key in keys) and \
                not any(anti_key.upper() in name for anti_key in anti_keys):
                    gpu['variants'].append(info)
    print("GPU Loading complete...")
    with open('MainData\gpu_data.json', 'w', encoding='utf-8') as f:
        json.dump(gpu_data, f, ensure_ascii=False, indent=4)
                   
    return gpu_data