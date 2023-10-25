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
import re
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

def get_keys_from_name_intel(processor_number: str, product_collection: str) -> list[str]:
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
    cpu_data['keys'] = get_keys_from_name_intel(cpu_data['processor_number'], cpu_data['product_collection'])

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
    
def map_sockets_to_chipsets_intel(cpu_data_filename: str = f'{get_path_of_data_folder()}/specifications/cpu_data_intel.json') -> dict:
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
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
def selenium_scrape_amd() -> list[BeautifulSoup]:
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    wait_condition = EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content'))
    url = 'https://www.amd.com/en/products/specifications/processors'
    data = []
    pbar = tqdm(desc="Scraping cpu urls. Pages Scraped", unit=" pages", dynamic_ncols=True)
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        WebDriverWait(driver, 15).until(wait_condition)
        time.sleep(4)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_cookies_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_cookies_button.click()
        except TimeoutException:
            print("Accept cookies button not found or was not clickable. Proceeding without accepting.")
        time.sleep(4)
        while True: 
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            cpus = soup.find_all('tr', attrs={"data-index": True})
            if set(cpus).issubset(data):
                pbar.close()
                break
            data.extend(cpus)
            pbar.update(1)  
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '.page-next:not(.disabled)')
                next_button.click()
                WebDriverWait(driver, 10).until(wait_condition)
            except NoSuchElementException:
                pbar.close()  
                break
    finally:
        driver.quit()
    return data

def get_urls_amd() -> list[str]:
    soups = selenium_scrape_amd()
    urls = []
    for soup in soups:
        url = 'https://www.amd.com/'+soup.find_all('a')[1]['href']
        urls.append(url)
    return urls

def selenium_scrape(url):
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--start-timeout=3")
    driver = webdriver.Firefox(options=firefox_options)
    time.sleep(1)
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        WebDriverWait(driver, 7).until(EC.visibility_of_element_located((By.CLASS_NAME, 'path-product')))
        time.sleep(1)
        try:
            WebDriverWait(driver, 7).until(EC.visibility_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            accept_cookies_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_cookies_button.click()
        except TimeoutException:
            print("Accept cookies button not found or was not clickable. Proceeding without accepting.")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    finally:
        driver.quit()
    return soup

def match_class(target):
    if target:
        classes = ' '.join(target)
        return classes.startswith('field field')
    return False

def get_keys_from_name_amd(name: str) -> list[str]:
    name = name.replace('-', ' ').lower()
    keys = [word.lower() for word in name.split()]
    anit_words = ['amd', 'radeon', 'with', '(',')', 'only', 'graphics','oem',"and","near","silent","thermal","solution","series","wraith","cooler"]
    for word in anit_words:
        if word in keys:
            keys.remove(word)
    return keys

def scrape_cpu_url_amd(url: str) -> dict:
    soup = selenium_scrape(url)
    soup_name = soup.find('div', id='block-amd-page-title')
    name = soup_name.find('h2').get_text().replace('\u2122', '')
    keys = get_keys_from_name_amd(name)
    pattern = re.compile(r'field field--name-[^ ]+')
    divs = soup.find_all('div', class_=True)
    cpu_data = {}
    cpu_data['url'] = url
    cpu_data['name'] = name
    cpu_data['keys'] = keys
    for div in divs:
        class_string = ' '.join(div['class'])
        if pattern.search(class_string):
            inner_soup = BeautifulSoup(str(div), 'html.parser')
            label = inner_soup.find('div', class_='field__label')
            data_items = inner_soup.find_all('div', class_='field__item')
            def process_data(item_text: str) -> str:
                item_text = item_text.strip().lower()
                #'\u00b2','\u2122','\u00b0','\u00b1','\u00ae'   replace with ''
                item_text = item_text.replace('\u2122', '').replace('\\', '').replace('"', '').replace('\u00b2', '').replace('\u00b0', '').replace('\u00b1', '').replace('\u00ae', '').replace('up_to_', '')
                if item_text == 'yes':
                    return True
                elif item_text == 'no':
                    return False
                return item_text.replace('\n', '').replace(' ', '_')
            if len(data_items) > 1:
                data = [process_data(item.get_text()) for item in data_items]
            elif data_items:
                data = process_data(data_items[0].get_text())
            else:
                data = None
            if label and data:
                label = process_data(label.get_text())
                cpu_data[label] = data
    return cpu_data

def get_cpu_data_amd() -> list[dict]:
    cpu_urls = get_urls_amd()
    
    file_path = f'{get_path_of_data_folder()}/specifications/cpu_data_amd.json'
    cpu_data = load_data(file_path)
    if cpu_data:
        existing_urls = {cpu['url'] for cpu in cpu_data}
    else:
        existing_urls = set()
        cpu_data = []
    
    for url in tqdm(cpu_urls, desc="Scraping CPU data", unit="cpu"):
        if url not in existing_urls:
            try:
                cpu_info = scrape_cpu_url_amd(url)
                if cpu_info:  # checking if data is valid before appending
                    cpu_data.append(cpu_info)
                    save_data(cpu_data, file_path)  # save data after each successful scrape
                    existing_urls.add(url)
            except Exception as e:
                print(f"Error scraping URL {url}: {e}")

    return cpu_data

def temp_fix_data():
    def remove_special_chars(s):
        chars_to_remove = ['\\', '"', '\u00b2', '\u2122', '\u00b0', '\u00b1', '\u00ae']
        for char in chars_to_remove:
            s = s.replace(char, '')
        return s
    def clean_dictionary(d):
        return {remove_special_chars(key): remove_special_chars(value) if isinstance(value, str) else value for key, value in d.items()}
    data = load_data(f'{get_path_of_data_folder()}/specifications/cpu_data_amd.json')
    new_data = []
    for cpu in data:
        anit_words = ['amd', 'radeon', 'with', '(',')', 'only', 'graphics','oem',"and","near","silent","thermal","solution","series"]
        for word in anit_words:
            if word in cpu['keys']:
                cpu['keys'].remove(word)
        if len(cpu['keys']) == 1:
            new_keys = cpu['product_family'].replace('_', ' ').lower().split()
            for key in new_keys:
                if key not in cpu['keys']:
                    cpu['keys'].append(key)
        cpu = clean_dictionary(cpu)
        new_data.append(cpu)
    save_data(new_data, f'{get_path_of_data_folder()}/specifications/cpu_data_amd2.json')

def map_sockets_to_chipsets_amd(cpu_data_filename: str = f'{get_path_of_data_folder()}/specifications/cpu_data_amd.json') -> dict:
    data = load_data(cpu_data_filename)
    sockets_to_chipsets = {}
    for cpu in data:
        if 'cpu_socket' not in cpu or 'supporting_chipsets' not in cpu:
            continue
        socket = cpu['cpu_socket'] 
        for chipset in cpu['supporting_chipsets']:
            if socket in sockets_to_chipsets:
                if chipset not in sockets_to_chipsets[socket]:
                    sockets_to_chipsets[socket].append(chipset)
            else:
                sockets_to_chipsets[socket] = [chipset]
    return sockets_to_chipsets


def standardize_data():
    amd_data = load_data(f'{get_path_of_data_folder()}/specifications/cpu_data_amd.json')
    intel_data = load_data(f'{get_path_of_data_folder()}/specifications/cpu_data_intel.json')
    naming_mapping = {
        'url': ['url'],  
        'name': ['name', 'processor_number'],  
        'product_collection': ['product_collection', 'product_family'],
        'platform': ['platform', 'vertical_segment'],
        'total_cores': ['total_cores', '#_of_cpu_cores'],
        'total_threads': ['total_threads', '#_of_threads'],
        'code_name': ['code_name', 'former_codename'],
        'turbo_frequency': ['max_turbo_frequency', 'max._boost_clock'],
        'tdp': ['processor_base_power', 'default_tdp'],
        'socket': ['cpu_socket', 'sockets_supported'],
        'launch_data': ['launch_date', 'launch_date'],
        'max_memory': ['max._memory', 'max_memory_size_(dependent_on_memory_type)'],
        'memory_types': ['memory_types', 'system_memory_type'],
        'memory_channels': ['max_#_of_memory_channels', 'memory_channels'],
        'ecc_memory_support': ['ecc_memory_supported', 'ecc_support'],
        'processor_graphics': ['processor_graphics', 'integrated_graphics'],
        'thermal_limit': ['tjunction', 'max._operating_temperature_(tjmax)'],
        'pcie_revision': ['pci_express_revision', 'pci_express_version'],
        'chipsets': ['supporting_chipsets', 'chipsets']
    }
    
    standardized_data = []

    for cpu in amd_data + intel_data:
        standardized_cpu = dict(cpu)

        for standard_name, possible_names in naming_mapping.items():
            for possible_name in possible_names:
                if possible_name in cpu:
                    standardized_cpu[standard_name] = cpu[possible_name]
                    if standard_name != possible_name:
                        del standardized_cpu[possible_name]
                    break

        standardized_data.append(standardized_cpu)

    return standardized_data
        
def update_cpu_data_intel(path=f'{get_path_of_data_folder()}/specifications/cpu_data_intel.json') -> None:
    save_data(get_cpu_data_intel(), path)

def update_cpu_data_amd(path=f'{get_path_of_data_folder()}/specifications/cpu_data_amd.json') -> None:
    save_data(get_cpu_data_amd(), path)

def update_cpu_data_standardized(path=f'{get_path_of_data_folder()}/specifications/cpu_data_standardized.json') -> None:
    save_data(standardize_data(), path)

def update_chipset_socket_mapping(path=f'{get_path_of_data_folder()}/specifications/chipset_socket_mapping.json') -> None:
    intel_chipset_map = map_sockets_to_chipsets_intel()
    amd_chipset_map = map_sockets_to_chipsets_amd()
    combined = {**intel_chipset_map, **amd_chipset_map}
    save_data(combined, path)

def update_cpu_data_all() -> None:
    update_cpu_data_intel()
    update_cpu_data_amd()
    update_cpu_data_standardized()
    update_chipset_socket_mapping()