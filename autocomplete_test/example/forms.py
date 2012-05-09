from django import forms

from autocomplete_test.example.models import Example, Value
from jautocomplete.widgets import SelectAutocompleteInput, ComboAutocompleteInput
from jautocomplete.fields  import ComboModelChoiceField

class TestForm(forms.ModelForm):
    class Meta:
        model = Example
        widgets = {
            "value": SelectAutocompleteInput()
        }
        
class ComboForm(forms.ModelForm):
    value = ComboModelChoiceField(queryset=Value.objects.all(), widget=ComboAutocompleteInput)
    class Meta:
        model = Example