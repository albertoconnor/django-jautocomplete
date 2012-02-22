from django import forms

from autocomplete_test.example.models import Example
from jautocomplete.widgets import SelectAutocompleteInput

class TestForm(forms.ModelForm):
    class Meta:
        model = Example
        widgets = {
            "value": SelectAutocompleteInput()
        }