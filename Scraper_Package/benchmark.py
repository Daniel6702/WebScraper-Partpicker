import requests
import os
from bs4 import BeautifulSoup
import json

def get_path_of_data_folder():
    return os.path.join(os.path.dirname(__file__), '..', 'Data')

def download_userbenchmark(data_path=get_path_of_data_folder()):
    folder_path = data_path + "/benchmarks"
    urls = ["https://www.userbenchmark.com/resources/download/csv/GPU_UserBenchmarks.csv",
           "https://www.userbenchmark.com/resources/download/csv/CPU_UserBenchmarks.csv"]
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for url in urls:
        response = requests.get(url)
        filename = url.split("/")[-1]
        if response.status_code == 200:
            with open(os.path.join(folder_path, filename), "wb") as file:
                file.write(response.content)
            print(f"Downloaded {filename} to {folder_path}")
        else:
            print(f"Failed to retrieve the data from {url}")

def scrape_geekbench_cpu(data_path=get_path_of_data_folder()):
    folder_path = data_path + "/benchmarks"
    page = requests.get('https://browser.geekbench.com/processor-benchmarks/')
    soup = BeautifulSoup(page.content, "html.parser")
    cpus = soup.find_all('tr')
    cpu_data = []
    for cpu in cpus[1:]: 
        cpu_name_tag = cpu.find('a', href=True)  
        if cpu_name_tag is not None:
            name = cpu_name_tag.text.strip().replace("-", " ").lower()
        score = cpu.find('td', class_='score')
        if score is not None:
            score = score.text.strip()
        cpu_data.append({'name': name, 'score': score})
    with open(os.path.join(folder_path, 'geekbench_cpu.json'), 'w', encoding='utf-8') as f:
        json.dump(cpu_data, f, ensure_ascii=False, indent=4)

def scrape_geekbench_gpu(data_path=get_path_of_data_folder()):
    folder_path = data_path + "/benchmarks"
    page = requests.get('https://browser.geekbench.com/opencl-benchmarks')
    soup = BeautifulSoup(page.content, "html.parser")
    gpus = soup.find_all('tr')
    gpu_data = []
    for cpu in gpus[1:]: 
        cpu_name_tag = cpu.find('td', class_='name')  
        if cpu_name_tag is not None:
            name = cpu_name_tag.text.strip().replace("-", " ").lower()
        score = cpu.find('td', class_='score')
        if score is not None:
            score = score.text.strip()
        gpu_data.append({'name': name, 'score': score})
    with open(os.path.join(folder_path, 'geekbench_gpu.json'), 'w', encoding='utf-8') as f:
        json.dump(gpu_data, f, ensure_ascii=False, indent=4)

