import json
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def scrape(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")

def selenium_scrape(url,wait_condition):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        WebDriverWait(driver, 7).until(wait_condition)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()
    return soup

def scrape_chipsets_intel() -> list[dict]:
    soup = scrape('https://www.intel.com/content/www/us/en/products/details/chipsets/desktop-chipsets/products.html')
    chipset_html = soup.find_all('tr', attrs={"data-filter-ddlviewselection": True})
    chipsets = []
    for chipset_soup in chipset_html:
        url = chipset_soup.find('td').find('a')['href']
        data_values = [td['data-value'] for td in chipset_soup.find_all('td', attrs={'data-value': True})]
        chipsets.append(
            {'name': data_values[0], 
             'overclocking': data_values[1] if data_values[1] != '' else False, 
             'pci_revision': [int(float(i)) for i in data_values[2].split(',') if '.' in i or i.strip().isdigit()],
             'usb_revision': [float(i) for i in data_values[3].replace('/', ',').split(',') if '.' in i or i.strip().isdigit()],
             'tdp': data_values[4],
             'url': 'https://www.intel.com'+url
            })
    return chipsets

def get_urls_from_chipset_intel(chipset_url: str) -> list[str]:
    url = chipset_url[:-len("/specifications.html")] + "/compatible.html" if chipset_url.endswith("/specifications.html") else chipset_url
    soup = scrape(url)
    chipset_html = soup.find_all('tr', attrs={"data-product-id": True})
    cpu_urls = []
    for cpu_soup in chipset_html:
        url = 'https://www.intel.com'+cpu_soup.find('div', class_='add-compare-wrap').find('a')['href']
        cpu_urls.append(url)
    return cpu_urls

def get_keys_from_name(processor_number: str, product_collection: str) -> list[str]:
    processor_number = processor_number.replace('-', ' ')
    keys = [word.lower() for word in processor_number.split()]
    keywords = ['celeron', 'pentium', 'core', 'xeon']
    for keyword in keywords:
        if keyword in product_collection:
            keys.append(keyword)
            break
    return keys	

def scrape_cpu_url_intel(url: str) -> dict:
    def clean_string(s: str) -> str:
        for old, new in [('\n', ''), (' ', '_'), ('intel\u00ae ', ''), 
                        ('intel\u00ae', ''), (' \u2021', ''), ('\u2021', ''), 
                        ('\u2122', ''), ('\u00ae', '')]:
            s = s.replace(old, new)
        return s.strip('_')
    def normalize_values(value):
        if value.lower() in ['yes', 'no']:
            return True if value.lower() == 'yes' else False
        return value
    soup = scrape(url)
    rows = soup.find_all('div', class_='row tech-section-row')
    cpu_data = {'url': url}

    for row in rows:
        label = row.find('div', class_='col-xs-6 col-lg-6 tech-label').get_text()
        data = row.find('div', class_='col-xs-6 col-lg-6 tech-data').get_text()
        label, data = clean_string(label.lower()), clean_string(data.lower())
        cpu_data[label] = normalize_values(data)

    if 'sockets_supported' in cpu_data:
        cpu_data['sockets_supported'] = cpu_data['sockets_supported'].replace('fc', '')
    cpu_data['keys'] = get_keys_from_name(cpu_data['processor_number'], cpu_data['product_collection'])

    return cpu_data

def get_cpu_data_intel() -> list[dict]:
    cpu_url_to_chipsets = {}
    cpu_data = []

    chipsets = scrape_chipsets_intel()

    for chipset in tqdm(chipsets, desc="Processing chipsets", unit="chipset"):
        new_urls = get_urls_from_chipset_intel(chipset['url'])
        for url in new_urls:
            if url in cpu_url_to_chipsets:
                cpu_url_to_chipsets[url].append(chipset['name'])  
            else:
                cpu_url_to_chipsets[url] = [chipset['name']]

    for url, chipset_names in tqdm(cpu_url_to_chipsets.items(), desc="Scraping CPU data", unit="cpu"):
        cpu_info = scrape_cpu_url_intel(url)
        cpu_info['chipsets'] = chipset_names  
        cpu_data.append(cpu_info)

    return cpu_data

def get_path_of_data_folder():
    return os.path.join(os.path.dirname(__file__), '..', 'Data')

def save_data(data: list[dict], filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def load_data(filename: str) -> list[dict]:
    with open(filename, 'r') as f:
        return json.load(f)
    
def map_sockets_to_chipsets(cpu_data_filename: str = f'{get_path_of_data_folder()}/specifications/cpu_data.json') -> dict:
    data = load_data(cpu_data_filename)
    sockets_to_chipsets = {}
    for cpu in data:
        if 'sockets_supported' not in cpu or 'chipsets' not in cpu:
            continue
        socket = cpu['sockets_supported'] 
        for chipset in cpu['chipsets']:
            if socket in sockets_to_chipsets:
                if chipset not in sockets_to_chipsets[socket]:
                    sockets_to_chipsets[socket].append(chipset)
            else:
                sockets_to_chipsets[socket] = [chipset]
    return sockets_to_chipsets

def scrape_cpu_urls_amd() -> list[BeautifulSoup]:
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    wait_condition = EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content'))
    url = 'https://www.amd.com/en/products/specifications/processors'
    data = []

    try:
        driver.get(url)
        driver.implicitly_wait(100)
        WebDriverWait(driver, 15).until(wait_condition)
        time.sleep(8)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_cookies_button.click()
        except TimeoutException:
            print("Accept cookies button not found or was not clickable. Proceeding without accepting.")
        time.sleep(8)

        while True: 
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cpus = soup.find_all('tr', attrs={"data-index": True})
            if set(cpus).issubset(data):
                break
            data.extend(cpus)
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '.page-next:not(.disabled)')
                next_button.click()
                WebDriverWait(driver, 15).until(wait_condition)
            except NoSuchElementException:
                break
    finally:
        driver.quit()
    return data

def get_urls_amd() -> list[str]:
    soups = scrape_cpu_urls_amd()
    urls = []
    for soup in soups:
        url = 'https://www.amd.com/'+soup.find('a')['href']
        urls.append(url)
    return urls
    
def main() -> None:
    save_data(get_cpu_data_intel(), f'{get_path_of_data_folder()}/specifications/cpu_data.json')
    save_data(map_sockets_to_chipsets(), f'{get_path_of_data_folder()}/specifications/socket_chipset_map.json')

print("start")
get_urls_amd()
print("done")