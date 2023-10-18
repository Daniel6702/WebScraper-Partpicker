from django import forms

class ScraperForm(forms.Form):
    budget = forms.CharField(label='Budget', max_length=500)

class BudgetForm(forms.Form):
    lower_budget = forms.IntegerField()
    upper_budget = forms.IntegerField()

class PCBuilderForm(forms.Form):
    USAGE_CHOICES = [
        ('gaming', 'Gaming'),
        ('productivity', 'Productivity'),
        ('streaming', 'Streaming'),
        ('vr', 'VR'),
    ]
    usage = forms.MultipleChoiceField(choices=USAGE_CHOICES, widget=forms.CheckboxSelectMultiple)

