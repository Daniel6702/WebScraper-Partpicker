from django import forms

class ScraperForm(forms.Form):
    budget = forms.CharField(label='Budget', max_length=500)