import csv
from tqdm import tqdm
import re
from url_fetcher import ProductURLFetcher
import scraper
import json

def get_names(csv_filepath):
    names = []
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            model = row['Model']
            names.append(model.replace('-', ' '))
    return names

def get_keys(name):
    keys = [word.lower() for word in name.split()]
    return keys
    
def create_id(name):
    name_hash = hash(name)
    random_id = abs(name_hash)
    return random_id

def get_performance(keys, csv_filepath):
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            model = row['Model'].upper()
            benchmark = row['Benchmark']
            if match(model, keys):
                benchmark = float(benchmark)
                if benchmark > 150:
                    benchmark /= 10
                return benchmark
            
def match(name, keys):
    if all(re.search(r'\b' + re.escape(key.upper()) + r'\b', name) for key in keys):
        return True
                 
def get_cpu_data():
    cpu_data = []
    names = get_names("BenchmarkData\CPU_UserBenchmarks.csv")
    for name in tqdm(names, desc="Loading CPU Specs", unit="spec"):
        keys = get_keys(name)
        id = create_id(name)
        benchmark = get_performance(keys, "BenchmarkData\CPU_UserBenchmarks.csv")
        data = {
            "name": name,
            "keys": keys,
            "anti_keys": [],
            "id": id,
            "performance": benchmark,
            "variants": []
        }
        cpu_data.append(data)
    cpu_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        cpu_urls += ProductURLFetcher.from_source(source, 'cpu').get_product_urls()
    for url in tqdm(cpu_urls, desc="Scraping Data", unit="url"):
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
            for cpu in cpu_data:
                keys = cpu['keys']
                if match(name, keys):
                    cpu['variants'].append(info)  
    print("CPU Loading complete...")
    with open('MainData\cpu_data.json', 'w', encoding='utf-8') as f:
        json.dump(cpu_data, f, ensure_ascii=False, indent=4)
    return cpu_data


get_cpu_data()