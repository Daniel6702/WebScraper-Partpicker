from django.shortcuts import render,redirect
from .forms import ScraperForm
from Scraper_Package.picker import select_components
from .forms import PCBuilderForm
from django.http import HttpResponseRedirect

def pc_builder(request):
    if request.method == 'POST':
        form = PCBuilderForm(request.POST)
        if form.is_valid():
            # Process and save the data
            # For example, you can filter out PC builds based on the form data
            # and display them on a new results page.
            return redirect('pc_build_results')
    else:
        form = PCBuilderForm()
    return render(request, 'scraper_webapp/pc_builder.html', {'form': form})