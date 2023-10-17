from url_fetcher import ProductURLFetcher
import scraper
import re
import csv
import json
from tqdm import tqdm
from dataclasses import asdict
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

def update_all_data():
    RAM().retrieve_data()
    PSU().retrieve_data()
    Motherboards().retrieve_data()
    Drives().retrieve_data()
    Coolers().retrieve_data()
    Cases().retrieve_data()
    GPU().retrieve_data()
    CPU().retrieve_data()

class LoadData():
    def __init__(self, category, sources):
        self.category = category
        self.sources = sources
        current_dir = os.path.dirname(os.path.abspath(__file__))  
        self.filepath = os.path.join(current_dir, 'MainData')  
        self.benchmark_filepath = os.path.join(current_dir, 'BenchmarkData')

    def load_urls(self):
        product_urls = []
        for source in tqdm(self.sources, desc="Loading URLs", unit="source"):
            product_urls += ProductURLFetcher.from_source(source, self.category).get_product_urls()
        return product_urls
    
    def load_product_info(self):
        urls = self.load_urls()
        infos = []
        for url in tqdm(urls, desc="Scraping Data", unit="url"):
            info = scraper.get_website_handler(url).get_product_info()
            infos.append(info)
        return infos
    
    def retrieve_data(self):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def save_data(self,data):
        with open(f'{self.filepath}\\{self.category}_data.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def create_id(self,name):
        name_hash = hash(name)
        random_id = abs(name_hash)
        return random_id
    
class RAM(LoadData):
    def __init__(self):
        super().__init__('ram', ['proshop', 'komplett', 'computersalg'])
    
    def retrieve_data(self):
        ram_data = []
        infos = self.load_product_info()
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            if info.name is None:
                continue
            specs = self.extract_ram_info(info.name)
            performance = self.calculate_ram_performance(specs['Capacity'], specs['MHz'], specs['Number of Sticks'])
            ram_data.append(asdict(info))
            ram_data[-1]['performance'] = performance
            ram_data[-1].update(specs)
        self.save_data(ram_data)

    def extract_ram_info(self,product_name):
        capacity_pattern = r'(\d+)\s?GB'
        mhz_pattern = r'(\d+)\s?Mhz'
        type_pattern = r'DDR[0-9]+'
        sticks_pattern = r'(\d+)\s?x\s(\d+)\s?GB'
        alt_mhz_pattern = r'DDR[0-9]+-(\d+)\s?'

        capacity_match = re.search(capacity_pattern, product_name)
        capacity = int(capacity_match.group(1)) if capacity_match else None

        mhz_match = re.search(mhz_pattern, product_name, re.IGNORECASE)
        mhz = int(mhz_match.group(1)) if mhz_match else None

        if not mhz:
            alt_mhz_match = re.search(alt_mhz_pattern, product_name, re.IGNORECASE)
            mhz = int(alt_mhz_match.group(1)) if alt_mhz_match else None

        type_match = re.search(type_pattern, product_name)
        ram_type = type_match.group() if type_match else None

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
    
    def calculate_ram_performance(self,capacity, mhz, num_sticks):
        capacity_weight = 0.4
        mhz_weight = 0.4
        num_sticks_weight = 0.2

        performance = 0.0

        if capacity is not None and mhz is not None:
            normalized_capacity = capacity / 32  # Assuming a maximum of 32GB
            normalized_mhz = mhz / 6400
            normalized_num_sticks = num_sticks / 4

            performance = (
                normalized_capacity * capacity_weight +
                normalized_mhz * mhz_weight +
                normalized_num_sticks * num_sticks_weight
            )

        return performance
    
class PSU(LoadData):
    def __init__(self):
        super().__init__('psu', ['proshop', 'komplett', 'computersalg'])

    def extract_wattage(self,name):
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

    def retrieve_data(self):
        psu_data = []
        infos = self.load_product_info()
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            if info.name is None:
                continue
            wattage = self.extract_wattage(info.name)
            if wattage is None:
                continue
            psu_data.append(asdict(info))
            psu_data[-1]['wattage'] = self.extract_wattage(info.name)
        self.save_data(psu_data)
    
class Motherboards(LoadData):
    def __init__(self):
        super().__init__('bundkort', ['proshop', 'komplett', 'computersalg'])

    def retrieve_data(self):
        infos = self.load_product_info()
        motherboard_data = []
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            if info.name is None:
                continue
            motherboard_data.append(asdict(info))
            motherboard_data[-1].update(self.extract_motherboard_info(info.name))
        self.save_data(motherboard_data)

    def extract_motherboard_info(self,name):
        with open('util_data.json', 'r') as f:
            data = json.load(f)
            cpu_sockets = data['sockets']
            chipsets = data['chipsets']
            ram_types = data['ram_types']
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
    
class Drives(LoadData):
    def __init__(self):
        super().__init__('drives', ['proshop', 'computersalg'])

    def retrieve_data(self):
        drive_data = []
        infos = self.load_product_info()
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            specs = self.retrieve_drive_info(info.name)
            if specs['capacity'] is None or specs['type'] is None or specs['interface'] is None:
                continue
            drive_data.append(asdict(info))
            drive_data[-1].update(specs)
        self.save_data(drive_data)

    def retrieve_drive_info(self,product_name):
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
    
class Coolers(LoadData):
    def __init__(self):
        super().__init__('cpu_cooler', ['proshop'])

    def retrieve_data(self):
        cooler_data = []
        urls = self.load_urls()
        for url in tqdm(urls, desc="Scraping Data", unit="url"):
            info = asdict(scraper.get_website_handler(url).get_product_info())
            description = self.extract_cpu_cooler_info(url)
            specs = self.get_cpu_cooler_data(description)        
            if specs['supported_sockets'] == []:
                continue
            info.update(specs)
            cooler_data.append(info)
        self.save_data(cooler_data)

    def extract_cpu_cooler_info(self,url):
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

    def get_cpu_cooler_data(self,description: str):
        with open('util_data.json', 'r') as f:
            cpu_sockets = json.load(f)['sockets']
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

class Cases(LoadData):
    def __init__(self):
        super().__init__('cases', ['proshop', 'komplett', 'computersalg'])

    def retrieve_data(self):
        cases_data = []
        infos = self.load_product_info()
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            size = self.retrieve_case_info(info.name)
            if size is None:
                continue
            cases_data.append(asdict(info))
            cases_data[-1]['size'] = size
        self.save_data(cases_data)

    def retrieve_case_info(self,product_name):
        size = None
        product_name = product_name.lower()
        if 'minitower' in product_name or 'mini tower' in product_name or 'mini' in product_name:
            size = 'Mini Tower'
        elif 'miditower' in product_name or 'mid tower' in product_name or 'midi tower' in product_name:
            size = 'Mid Tower'
        elif 'fulltower' in product_name or 'full tower' in product_name:
            size = 'Full Tower'
        return size

class GPU(LoadData):
    def __init__(self):
        super().__init__('grafikkort', ['proshop', 'komplett', 'computersalg'])

    def retrieve_data(self):
        gpu_data = []  
        for name in self.get_names(f'{self.benchmark_filepath}\\GPU_UserBenchmarks.csv'):
            data = {
                "name": name,
                "keys": self.get_keys(name),
                "anti_keys": self.get_anti_keys(name),
                "id": self.create_id(name),
                "performance": self.get_performance(self.get_keys(name), self.get_anti_keys(name), f'{self.benchmark_filepath}\\GPU_UserBenchmarks.csv'),
                "variants": []
            }
            gpu_data.append(data)
        infos = self.load_product_info()
        for info in tqdm(infos, desc="Processing Data", unit="product"):
            if info.name is None:
                continue
            for gpu in gpu_data:
                keys, anti_keys = map(str.upper, gpu['keys']), map(str.upper, gpu['anti_keys'])  # Using map to apply 'upper' to all elements
                name_upper = info.name.upper()
                if all(key in name_upper for key in keys) and not any(anti_key in name_upper for anti_key in anti_keys):
                    gpu['variants'].append(asdict(info))
        self.save_data(gpu_data)

    def get_names(self,csv_filepath):
        names = []
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                brand = row['Brand']
                model = row['Model']
                if brand in ['Nvidia', 'AMD']:
                    names.append(model.replace('-', ' '))
        return names

    def get_anti_keys(self,name):
        anti_keys = []
        name_upper = name.upper()
        if ("RTX" in name_upper or "GTX" in name_upper) and "TI" not in name_upper:
            anti_keys.append("ti")
        elif "RX" in name_upper and "XT" not in name_upper and "XTX" not in name_upper:
            anti_keys.extend(["xt", "xtx"])
        elif " HD " in name_upper:
            anti_keys.append("rx")
        return anti_keys

    def get_keys(self,name):
        stopwords = ["Nvidia", "AMD", "Intel"]
        keys = [word.lower() for word in name.split() if word not in stopwords]
        keys = [key.replace("(", "").replace(")", "") for key in keys]
        keys = [" " + key + " " for key in keys]
        return keys

    def get_performance(self,keys,anti_keys,csv_filepath):
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                model = row['Model'].upper()
                benchmark = row['Benchmark']
                if all(key.upper() in model for key in keys) and \
                not any(anti_key.upper() in model for anti_key in anti_keys):
                    return benchmark


class CPU(LoadData):
    def __init__(self):
        super().__init__('cpu', ['proshop', 'komplett', 'computersalg'])

    def retrieve_data(self):
        cpu_data = [] 
        for name in self.get_names(f'{self.benchmark_filepath}\\CPU_UserBenchmarks.csv'):
            keys = self.get_keys(name)
            cpu_data.append({
                "name": name,
                "keys": keys,
                "anti_keys": [], 
                "id": self.create_id(name),
                "performance": self.get_performance(keys, f'{self.benchmark_filepath}\\CPU_UserBenchmarks.csv'),
                "variants": [],
                "socket": None 
            })

        for info in tqdm(self.load_product_info(), desc="Processing Data", unit="product"):
            if info.name is None:
                continue
            name_upper = info.name.upper()
            for cpu in cpu_data:
                if self.match(name_upper, cpu['keys']):
                    cpu['variants'].append(asdict(info))

                    if cpu['socket'] is None:
                        socket_info = self.get_socket(info.name)
                        if socket_info is not None:
                            cpu['socket'] = socket_info

        for cpu in cpu_data:
            if cpu['socket'] is None:
                cpu['socket'] = "Unknown"

        self.save_data(cpu_data)

    def get_socket(self,name):
        with open(f'{os.path.dirname(os.path.abspath(__file__))}\\util_data.json', 'r') as f:
            cpu_sockets = json.load(f)['sockets']
        socket = next((socket for socket in cpu_sockets if socket.lower() in name.lower()), None)
        return socket

    def get_names(self,csv_filepath):
        names = []
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                model = row['Model']
                names.append(model.replace('-', ' '))
        return names

    def get_keys(self,name):
        keys = [word.lower() for word in name.split()]
        return keys

    def get_performance(self,keys, csv_filepath):
        with open(csv_filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                model = row['Model'].upper()
                benchmark = row['Benchmark']
                if self.match(model, keys):
                    benchmark = float(benchmark)
                    if benchmark > 150:
                        benchmark /= 10
                    return benchmark
                
    def match(self,name, keys):
        if all(re.search(r'\b' + re.escape(key.upper()) + r'\b', name) for key in keys):
            return True
        

CPU().retrieve_data()
#GPU().retrieve_data()
#Cases().retrieve_data()
#Drives().retrieve_data()
#Motherboards().retrieve_data()
#PSU().retrieve_data()
#RAM().retrieve_data()