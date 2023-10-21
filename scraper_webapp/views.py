from django.shortcuts import render,redirect
from Scraper_Package.picker import buildComputer
from .forms import PCBuilderForm
from django.http import HttpResponseRedirect
from django.http import JsonResponse



def pc_builder(request):
    computer = None
    if request.method == 'POST':
        form = PCBuilderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            computer = buildComputer()
            # Check if it's an Ajax request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                print("Ajax request")
                return JsonResponse({'computer': computer})
    else:
        form = PCBuilderForm()

    return render(request, 'scraper_webapp/pc_builder.html', {'form': form, 'computer': computer})