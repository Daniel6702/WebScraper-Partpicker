import requests
import os

def download_userbenchmark(folder_path):
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

   
