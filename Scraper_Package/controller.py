import benchmark
import cpu_spec_scraper
import os

def get_path_of_data_folder():
    return os.path.join(os.path.dirname(__file__), '..', 'Data')

class Controller():
    def __init__(self):
        data_path = get_path_of_data_folder()

    def update_benchmark(self,query) -> str:
        if query == "userbenchmark":
            benchmark.download_userbenchmark(self.data_path)
            return "Userbenchmark data updated"
        elif query == "geekbench":
            benchmark.scrape_geekbench_cpu(self.data_path)
            benchmark.scrape_geekbench_gpu(self.data_path)
            return "Geekbench data updated"
        else:
            return "Invalid query"

    def update_cpu_specs(self,query) -> str:
        if query == "all":
            cpu_spec_scraper.update_cpu_data_all()
            return "All CPU data updated"
        elif query == "intel":
            cpu_spec_scraper.update_cpu_data_intel()
            return "Intel CPU data updated"
        elif query == "amd":
            cpu_spec_scraper.update_cpu_data_amd()
            return "AMD CPU data updated"
        elif query == "mapping":
            cpu_spec_scraper.update_chipset_socket_mapping()
            return "Chipset-Socket mapping updated"
        else:
            return "Invalid query"
        
    

