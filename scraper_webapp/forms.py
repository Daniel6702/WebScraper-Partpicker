from django import forms

class PCBuilderForm(forms.Form):
    lower_budget = forms.IntegerField(required=True)
    upper_budget = forms.IntegerField(required=True)

    USAGE_CHOICES = [
        ('gaming', 'Gaming'),
        ('productivity', 'General Productivity'),
        ('server', 'Server or networking tasks'),
        ('streaming', 'Streaming'),
        ('vr', 'Virtual reality'),
        ('video_editing', 'Video Editing'),
        ('3d_modeling', '3D Modeling and CAD'), 
        ('graphic_design', 'Graphic design'),
        ('programming', 'Software development'),
        ('casual', 'Casual Use'),
    ]
    
    usage = forms.ChoiceField(choices=USAGE_CHOICES, widget=forms.Select(attrs={'class': 'form-control custom-select'}))

    small_form_factor = forms.BooleanField(required=False)
    rgb = forms.BooleanField(required=False)
    wireless_connectivity = forms.BooleanField(required=False)
    overclocking_capabilities = forms.BooleanField(required=False)
    
    cooling_capability = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range'}), required=False)
    aesthetics = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range'}), required=False)
    priority = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range'}), required=False)

    

    
