from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import re
import json

def retrieve_case_info(product_name):
    size = None
    product_name = product_name.lower()
    if 'minitower' in product_name or 'mini tower' in product_name or 'mini' in product_name:
        size = 'Mini Tower'
    elif 'miditower' in product_name or 'mid tower' in product_name or 'midi tower' in product_name:
        size = 'Mid Tower'
    elif 'fulltower' in product_name or 'full tower' in product_name:
        size = 'Full Tower'
    return size

def load_case_data():
    cases_urls = []
    sources = ['proshop', 'komplett', 'computersalg']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        cases_urls += ProductURLFetcher.from_source(source, 'cases').get_product_urls()
    cases_data = []
    for url in tqdm(cases_urls, desc="Scraping data", unit="case"):
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        size = retrieve_case_info(info['name'])
        if size is None:
            continue
        info['size'] = size
        cases_data.append(info)
    print("Case Loading complete...")
    with open('MainData\case_data.json', 'w', encoding='utf-8') as f:
        json.dump(cases_data, f, ensure_ascii=False, indent=4)
    return cases_data

load_case_data()