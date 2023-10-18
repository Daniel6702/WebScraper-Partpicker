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
    'cpu': 0.25,     
    'mb': 0.1,      
    'ram': 0.05,     
    'cooler': 0.05, 
    'gpu': 0.35,    
    'drive': 0.1,   
    'case': 0.05,   
    'psu': 0.05,    
}

def get_file_path(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, 'MainData', filename)

def get_component_data(filename):
    with open(get_file_path(filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def select_components(budget_distribution, budget=10000):
    cpu_data = get_component_data('cpu_data.json')
    cpu, socket = get_cpu_component(cpu_data, budget_distribution['cpu'] * budget)
    
    mb_data = get_component_data('motherboard_data.json')
    mb, ram_type = get_mb_component(mb_data, budget_distribution['mb'] * budget, socket)
    
    gpu = get_gpu_component(get_component_data('gpu_data.json'), budget_distribution['gpu'] * budget)
    ram = get_ram_component(get_component_data('ram_data.json'), budget_distribution['ram'] * budget, ram_type)
    drive = get_drive_component(get_component_data('drives_data.json'), budget_distribution['drive'] * budget)
    case = get_case_component(get_component_data('case_data.json'), budget_distribution['case'] * budget)
    psu = get_psu_component(get_component_data('psu_data.json'), budget_distribution['psu'] * budget)
    cooler = get_cooler_component(get_component_data('cpu_cooler_data.json'), budget_distribution['cooler'] * budget, socket)

    return {
        'cpu': asdict(cpu),
        'mb': asdict(mb),
        'ram': asdict(ram),
        'cooler': asdict(cooler),
        'gpu': asdict(gpu),
        'drive': asdict(drive),
        'case': asdict(case),
        'psu': asdict(psu),
    }

def get_cpu_component(cpu_list, cpu_budget):
    for cpu in cpu_list:
        if not cpu['variants']:
            continue
        lowest_price_variant = min(cpu['variants'], key=lambda variant: variant['price'])
        if lowest_price_variant['price'] <= cpu_budget:
            cpu_data = Component(cpu['name'], lowest_price_variant['price'], cpu['performance'], lowest_price_variant['url'])
            return cpu_data, cpu['socket']
    return None

def get_mb_component(mb_list, mb_budget, socket): #atm finds the motherboard that is closest to the budget. not the cheapest
    mb_list.sort(key=lambda mb: mb['price'], reverse=True)
    for mb in mb_list:
        if mb['socket'].replace(" ", "") == socket:
            if mb['price'] <= mb_budget:
                mb_data = Component(mb['name'], mb['price'], None, mb['url'])
                return mb_data, mb['ram_type']
    return None

def get_gpu_component(gpu_list, gpu_budget):
    for gpu in gpu_list:
        if not gpu['variants']:
            continue
        lowest_price_variant = min(gpu['variants'], key=lambda variant: variant['price'])
        if lowest_price_variant['price'] <= gpu_budget:
            gpu_data = Component(gpu['name'], lowest_price_variant['price'], gpu['performance'], lowest_price_variant['url'])
            return gpu_data
    return None

def get_ram_component(ram_list, ram_budget, ram_type):
    ram_list.sort(key=lambda ram: ram['performance'], reverse=True)
    for ram in ram_list:
        if ram['Type'] == ram_type:
            if ram['price'] <= ram_budget:
                ram_data = Component(ram['name'], ram['price'], ram['performance'], ram['url'])
                return ram_data
    return None

def get_drive_component(drive_list, drive_budget):
    def calculate_drive_value(drive, type_weight=0.4, capacity_weight=0.4, interface_weight=0.2):
        specs = {'type': drive['type'], 'capacity': drive['capacity'], 'interface': drive['interface']}
        type_scores = {'ssd': 12, 'hdd': 3}
        interface_scores = {'sata': 5, 'm.2': 10, 'usb': 1}
        type_ = specs.get('type', 'hdd').lower() 
        capacity = specs.get('capacity', 500)
        interface = specs.get('interface', 'sata').lower()
        if abs(type_weight + capacity_weight + interface_weight-1) > 0.0001:
            raise ValueError("The sum of type_weight, capacity_weight, and interface_weight must be 1")
        type_score = type_scores.get(type_, 0)
        interface_score = interface_scores.get(interface, 0)
        capacity_score = capacity / 500
        value_score = (type_weight * type_score) + (capacity_weight * capacity_score) + (interface_weight * interface_score)
        if interface == 'usb':
            value_score*=0.1
        return value_score
    drive_list.sort(key=lambda drive: calculate_drive_value(drive), reverse=True)
    for drive in drive_list:
        if drive['price'] <= drive_budget:
            drive_data = Component(drive['name'], drive['price'], calculate_drive_value(drive), drive['url'])
            return drive_data
    return None

def get_case_component(case_list, case_budget):
    case_list.sort(key=lambda case: case['price'], reverse=True)
    for case in case_list:
        if 'Mini' not in case['size'] and case['price'] <= case_budget:  
            case_component = Component(case['name'], case['price'], None, case['url'])
            return case_component
    return None

def get_psu_component(psu_list, psu_budget):
    psu_list.sort(key=lambda case: case['wattage'], reverse=True)
    for psu in psu_list:
        if psu['price'] <= psu_budget:
            psu_data = Component(psu['name'], psu['price'], None, psu['url'])
            return psu_data
    return None

def get_cooler_component(cooler_list, cooler_budget, socket):
    cooler_list.sort(key=lambda case: case['price'], reverse=True)
    for cooler in cooler_list:
        if socket.replace('-', ' ') in cooler['supported_sockets'] and cooler['price'] <= cooler_budget:
            cooler_data = Component(cooler['name'], cooler['price'], None, cooler['url'])
            return cooler_data
    return None    
    


my_dict = select_components(budget)
print(json.dumps(my_dict, indent=4))