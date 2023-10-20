from django.shortcuts import render,redirect
from Scraper_Package.picker import select_components
from .forms import PCBuilderForm
from django.http import HttpResponseRedirect

def pc_builder(request):
    if request.method == 'POST':
        form = PCBuilderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            
    else:
        form = PCBuilderForm()
    return render(request, 'scraper_webapp/pc_builder.html', {'form': form})