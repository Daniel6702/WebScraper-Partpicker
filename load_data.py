from url_fetcher import ProductURLFetcher
import scraper
import re
import csv
import json

class LoadData():
    def __init__(self, category, sources):
        self.category = category
        self.sources = sources

    def load_urls(self):
        product_urls = []
        for source in self.sources:
            product_urls += ProductURLFetcher.from_source(source, self.category).get_product_urls()
        return product_urls
    
    def load_product_info(self):
        urls = self.load_urls()
        infos = []
        for url in urls:
            info = scraper.get_website_handler(url).get_product_info()
            infos.append(info)
        return infos
    
    def retrieve_data(self):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def save_data(self,data):
        with open(f'MainData\{self.category}_data.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def create_id(self,name):
        name_hash = hash(name)
        random_id = abs(name_hash)
        return random_id
        
class CPU(LoadData):
    def __init__(self):
        super().__init__('cpu', ['proshop', 'komplett', 'computersalg'])

    def retrieve_data(self):
        names = self.get_names("BenchmarkData\CPU_UserBenchmarks.csv")
        cpu_data = []
        for name in names:
            keys = self.get_keys(name)
            id = self.create_id(name)
            benchmark = self.get_performance(keys, "BenchmarkData\CPU_UserBenchmarks.csv")
            data = {
                "name": name,
                "keys": keys,
                "anti_keys": [],
                "id": id,
                "performance": benchmark,
                "variants": []
            }
            cpu_data.append(data)
        infos = self.load_product_info()
        for info in infos:
            if info['name'] == None:
                continue
            name = info['name'].upper()
            for cpu in cpu_data:
                keys = cpu['keys']
                if self.match(name, keys):
                    cpu['variants'].append(info)
        self.save_data(cpu_data)

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
        


