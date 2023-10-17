#Independent components: gpu, drive, case, psu
#cpu dependent components: cpu, mb, ram, cooler
import json
from dataclasses import dataclass, asdict
import os


@dataclass
class Component:
    name: str
    price: int
    performance: float
    url: str
    

budget = {
    'cpu': 0.2,     
    'mb': 0.1,      
    'ram': 0.1,     
    'cooler': 0.05, 
    'gpu': 0.35,    
    'drive': 0.1,   
    'case': 0.05,   
    'psu': 0.05,    
}

def get_component_list(path):
    with open(path, 'r') as f:
        return json.load(f)

def select_components(budget_distribution, budget=10000):
    current_dir = os.path.dirname(os.path.abspath(__file__))  
    main_path = os.path.join(current_dir, 'MainData')  
  
    cpu = get_cpu_component(get_component_list(os.path.join(main_path, 'cpu_data.json')),budget_distribution['cpu']*budget)
    #mb = get_mb_component(get_component_list('MainData\\motherboard_data.json'),budget['mb'], cpu['socket'])
    #ram = get_ram_component(get_component_list('MainData\\ram_data.json'),budget['ram'], mb['ram_type'])
    #cooler = get_cooler_component(get_component_list('MainData\\cpu_cooler_data.json'),budget['cooler'], cpu['socket'])
    #gpu = get_gpu_component(get_component_list('MainData\\gpu_data.json'),budget['gpu'])
    #drive = get_drive_component(get_component_list('MainData\\drive_data.json'),budget['drive'])
    #case = get_case_component(get_component_list('MainData\\case_data.json'),budget['case'])
    #psu = get_psu_component(get_component_list('MainData\\psu_data.json'),budget['psu'])

    return {
        'cpu': asdict(cpu),
        'mb': None,
        'ram': None,
        'cooler': None,
        'gpu': None,
        'drive': None,
        'case': None,
        'psu': None,
    }

def get_ram_component(ram_list, ram_budget, ram_type):
    pass

def get_cpu_component(cpu_list, cpu_budget):
    for cpu in cpu_list:
        cpu_info = {
            'name': cpu['name'],
            'socket': cpu['socket'],
            'performance': cpu['performance'],  
        }
        if not cpu['variants']:
            continue
        lowest_price_variant = min(cpu['variants'], key=lambda variant: variant['price'])
        if lowest_price_variant['price'] <= cpu_budget:
            cpu_info['variant'] = lowest_price_variant
            cpu_data = Component(cpu_info['name'], cpu_info['variant']['price'], cpu_info['performance'], cpu_info['variant']['url'])
            return cpu_data
    return None

        

def get_mb_component(mb_list, mb_budget, socket):
    pass

def get_gpu_component(gpu_list, gpu_budget):
    pass

def get_drive_component(drive_list, drive_budget):
    pass

def get_case_component(case_list, case_budget):
    pass

def get_psu_component(psu_list, psu_budget):
    pass

def get_cooler_component(cooler_list, cooler_budget, socket):
    pass

print(select_components(budget))