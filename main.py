import requests
import csv
import time
import json
from bs4 import BeautifulSoup
import gpu
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import scraper

from url_fetcher import ProductURLFetcher

'''
'grafikkort'
'cpu'
'ram'
'bundkort'
'psu'
'''

#https://www.computersalg.dk/i/9578305/asus-tuf-gaming-geforce-rtx-4070-ti-12gb-gddr6x
#url = 'https://www.computersalg.dk/i/7373225/gigabyte-nvidia-geforce-rtx-3060-vision-oc-12g-rev-2-0-grafikkort-gf-rtx-3060-12-gb-gddr6-pcie-4-0-x16-2-x-hdmi-2-x'
#website_handler = scraper.get_website_handler(url)
#info = website_handler.get_product_info()
#print(info)

#Info(name='ASUS RTX 4080 NOCTUA OC', price=12490.0, currency='DKK', id='1243372', valid=True)
#for every product in the database
#get product info
#standardize model name
#group by model name
#every model name has a list of products with prices and names, and cheapest product
#gpu.download_data_userbenchmark()

#names = gpu.get_names('GPU_UserBenchmarks.csv')
#gpu.add_to_json(names, 'products.json')
#benchmarks = gpu.load_benchmarks('GPU_UserBenchmarks.csv')
#gpu.match_and_update_performance('products.json',benchmarks)

#gpu.process_graphics_cards_data('products.json')

#<div data-js-pagination-list>
#gpu.scrape_komplett()
#gpu.get_proshop_gpu_urls()
#gpu.get_computersalt_gpu_urls(pages=20)

#print(gpu.get_proshop_gpu_urls())

#gpu_urls = ProductURLFetcher.from_proshop('grafikkort').get_product_urls() + \
#           ProductURLFetcher.from_komplett('grafikkort').get_product_urls() + \
#           ProductURLFetcher.from_computersalg('grafikkort').get_product_urls()
           
#print(gpu.load_gpu_data())

#print(len(gpu_urls))
gpu.load_gpu_data()