from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SeleniumScraper:
    def __init__(self, headless=True):
        firefox_options = webdriver.FirefoxOptions()
        if headless:
            firefox_options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=firefox_options)
    
    def scrape_product_urls(self, base_url, url_pattern, wait_condition, container_selector, 
                            link_selector, is_multi_page=False, pages=1):
        urls = []
        try:
            for page in range(1, pages + 1 if is_multi_page else 2):
                url = url_pattern.format(page)
                self.driver.get(url)
                self.driver.implicitly_wait(100)
                WebDriverWait(self.driver, 10).until(wait_condition)
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                products = soup.select(container_selector)
                for product in products:
                    a_tag = product.select_one(link_selector)
                    if a_tag:
                        product_url = a_tag['href']
                        absolute_url = urljoin(base_url, product_url)
                        urls.append(absolute_url)
        finally:
            self.driver.quit()
        return urls
    
class ProductURLFetcher:
    def __init__(self, base_url, url_pattern=None, wait_condition=None,
                 container_selector=None, link_selector=None, is_paginated=False, max_pages=None):
        self.base_url = base_url
        self.url_pattern = url_pattern
        self.wait_condition = wait_condition
        self.container_selector = container_selector
        self.link_selector = link_selector
        self.is_paginated = is_paginated
        self.max_pages = max_pages

    def get_product_urls(self):
        scraper = SeleniumScraper()
        return scraper.scrape_product_urls(self.base_url, self.url_pattern, self.wait_condition,
                                           self.container_selector, self.link_selector, 
                                           self.is_paginated, self.max_pages)
    
    def _category_interpreter(self, category_name):
        category_mappings = {
            'komplett': {
                'grafikkort': (10412, 'grafikkort'),
                'cpu': (11204, 'processorer'),
                'ram': (11209, 'hukommelse-ram'),
                'bundkort': (10111, 'bundkort'),
                'psu': (10057, 'stroemforsyninger'),
                'cpu_cooler': (10462, 'blaesere/koelere')
            },
            'computersalg': {
                'grafikkort': (5444, 'alle-grafikkort'),
                'cpu': (1482, 'processorer'),
                'ram': (1480, 'ram-hukommelse'),
                'bundkort': (1481, 'bundkort'),
                'psu': (1957, 'strømforsyning'),
                'cpu_cooler': (1338, 'cpu-køling')
            },
            'proshop': {
                'grafikkort': (None, 'Grafikkort'),
                'cpu': (None, 'CPU'),
                'ram': (None, 'RAM'),
                'bundkort': (None, 'Bundkort'),
                'psu': (None, 'Stroemforsyning'),
                'cpu_cooler': (None, 'CPU-Koeler')
            }
        }
        website_type = self.get_website_type()
        return category_mappings.get(website_type, {}).get(category_name, (None, None))
    
    def get_website_type(self):
        if 'komplett.dk' in self.base_url:
            return 'komplett'
        elif 'computersalg.dk' in self.base_url:
            return 'computersalg'
        elif 'proshop.dk' in self.base_url:
            return 'proshop'
        return None
    
    @classmethod
    def from_komplett(cls, category_name, hits=250):
        base_url = 'https://www.komplett.dk'
        instance = cls(base_url)
        category_number, category_name = instance._category_interpreter(category_name)
        url_pattern = (
            f'{base_url}/category/{category_number}/hardware/pc-komponenter/{category_name}'
            f'?hits={hits}&stockStatus=InStock&PendingRelease=false'
        )
        wait_condition = EC.visibility_of_element_located((By.CLASS_NAME, 'product-box-container'))
        container_selector = 'div.product-box-container'
        link_selector = 'a.product-link'
        return cls(base_url, url_pattern, wait_condition,
                   container_selector, link_selector)
    
    @classmethod
    def from_proshop(cls, category_name, pages=8):
        base_url = 'https://www.proshop.dk'
        instance = cls(base_url)
        _ , category_name = instance._category_interpreter(category_name)
        url_pattern = f'{base_url}/{category_name}?inv=1&pre=0&pn={{}}'
        wait_condition = EC.visibility_of_element_located((By.ID, 'siteContainer'))
        container_selector = 'li.row.toggle'
        link_selector = 'a.site-product-link'
        return cls(base_url, url_pattern, wait_condition, 
                   container_selector, link_selector, True, pages)
        
    @classmethod 
    def from_computersalg(cls, category_name, pages=8):
        base_url = 'https://www.computersalg.dk/'
        instance = cls(base_url)
        category_number, category_name = instance._category_interpreter(category_name)
        url_pattern = f'{base_url}l/{category_number}/{category_name}?page={{}}&sq=&csstock=1'
        wait_condition = EC.visibility_of_element_located((By.ID, 'MasterParentContainer'))
        container_selector = 'div[data-js-pagination-item]'
        link_selector = 'a'
        return cls(base_url, url_pattern, wait_condition, 
                   container_selector, link_selector, True, pages)
        
    @classmethod     
    def from_source(cls, source, category_name):
        if source == 'komplett':
            return ProductURLFetcher.from_komplett(category_name)
        elif source == 'proshop':
            return ProductURLFetcher.from_proshop(category_name)
        elif source == 'computersalg':
            return ProductURLFetcher.from_computersalg(category_name)
        return None