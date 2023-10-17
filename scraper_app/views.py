from django.shortcuts import render
from .forms import ScraperForm
from Scraper_Package.picker import select_components

budget_distribution = {
    'cpu': 0.2,     
    'mb': 0.1,      
    'ram': 0.1,     
    'cooler': 0.05, 
    'gpu': 0.35,    
    'drive': 0.1,   
    'case': 0.05,   
    'psu': 0.05,    
}

def scraper_view(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            budget = float(form.cleaned_data['budget'])
            dict_with_components_data = select_components(budget_distribution,budget)
            print(dict_with_components_data)

            return render(request, 'scraper_app/scraper.html', {'form': form})

    else:
        form = ScraperForm()

    return render(request, 'scraper_app/scraper.html', {'form': form})
