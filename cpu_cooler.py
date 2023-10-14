from url_fetcher import ProductURLFetcher
import scraper
from tqdm import tqdm
import json
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

x = ['https://www.proshop.dk/CPU-Koeler/Arctic-Silver-5-35g-Thermal-grease-Koelepasta/320746', 
     'https://www.proshop.dk/CPU-Koeler/be-quiet-Pure-Rock-Slim-2-CPU-Luftkoeler-Max-26-dBA/2969979', 
     'https://www.proshop.dk/CPU-Koeler/Arctic-Liquid-Freezer-II-240-CPU-Vandkoeling-Max-23-dBA/2816724', 
     'https://www.proshop.dk/CPU-Koeler/be-quiet-Dark-Rock-PRO-4-CPU-Luftkoeler-Max-24-dBA/2658250', 
     'https://www.proshop.dk/CPU-Koeler/Arctic-MX-6-thermal-paste-4-g-Koelepasta/3123862', 
     'https://www.proshop.dk/CPU-Koeler/Noctua-NH-D15-CPU-Luftkoeler-Max-24-dBA/2441505']

def extract_cpu_cooler_info(url):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    try:
        driver.get(url)
        driver.implicitly_wait(100)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'siteContainer')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        description = soup.find('p', {'class': 'site-product-short-description'}).text
    finally:
            driver.quit()
    return description
    
def get_cpu_cooler_data(description: str):
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
        "LGA 771",
        "LGA1700",
        "LGA1200",
        "LGA1151",
        "LGA2066",
        "LGA2011-v3",
        "LGA1150",
        "LGA1155",
        "LGA775",
        "LGA1356",
        "LGA2011",
        "LGA1366",
        "LGA771",
        "LGA1156"
    ]
    supported_sockets = []
    cooling_type = None
    if description is not None:
        for socket in cpu_sockets:
            if socket.lower() in description.lower():
                supported_sockets.append(socket)
        if 'luft' in description.lower() or 'air' in description.lower() or 'luftkøler' in description.lower() or 'luftkoeler' in description.lower() or 'luftkøling' in description.lower() or 'luftkuehler' in description.lower() or 'luftkuehlung' in description.lower() or 'luftkølet' in description.lower() or 'luftkuehlt' in description.lower() or 'luftkuehlte' in description.lower() or 'luftkølede' in description.lower():
            cooling_type = 'luft'
        elif 'vand' in description.lower() or 'water' in description.lower() or 'vandkøler' in description.lower() or 'wasserkuehler' in description.lower() or 'vandkøling' in description.lower() or 'wasserkuehlung' in description.lower() or 'vandkølet' in description.lower() or 'wassergekuehlt' in description.lower() or 'vandkølede' in description.lower() or 'wassergekuehlte' in description.lower() or 'vandkuehlt' in description.lower() or 'wassergekuehlt' in description.lower():
            cooling_type = 'vand'
    
    return {'supported_sockets': supported_sockets, 'cooling_type': cooling_type}

def load_cpu_cooler_data():
    cpu_cooler_urls = []
    sources = ['proshop']
    for source in tqdm(sources, desc="Loading URLs", unit="source"):
        cpu_cooler_urls += ProductURLFetcher.from_source(source, 'cpu_cooler').get_product_urls()
    cpu_cooler_data = []
    for url in tqdm(cpu_cooler_urls, desc="Scraping Data", unit="url"):
    
    #mix up the urls
    #import random
    #random.shuffle(cpu_cooler_urls)
    #cpu_cooler_urls = cpu_cooler_urls[:5]
    
    #for url in cpu_cooler_urls:
        info = scraper.get_website_handler(url).get_product_info()
        info = {
            "name": info.name,
            "price": info.price,
            "currency": info.currency,
            "id": info.id,
            "valid": info.valid,
            "url": url
        }
        description = extract_cpu_cooler_info(url)
        #print("description: ", description)
        specs = get_cpu_cooler_data(description)
        #print("specs: ", specs)
        
        if specs['supported_sockets'] == []:
            continue
        info.update(specs)
        cpu_cooler_data.append(info)
    print("CPU Cooler Loading complete...")
    with open('MainData\cpu_cooler_data.json', 'w', encoding='utf-8') as f:
        json.dump(cpu_cooler_data, f, ensure_ascii=False, indent=4)

load_cpu_cooler_data()