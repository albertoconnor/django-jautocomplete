from django import forms
from django.core.validators import EMPTY_VALUES

from jautocomplete.widgets import ComboInput

class ComboModelChoiceField(forms.ModelChoiceField):
    
    widget = ComboInput
    
    def new_object_from_value(self, value):
        """Override to change the behavior of transforming a novel value into
        a new instance of the model. Returned value will have .save() called on it
        """
        return self.queryset.model(name=value)
    
    def to_python(self, value):
        select_value, new_value = value
        if not new_value in EMPTY_VALUES:
            new_model = self.new_object_from_value(new_value)
            # Check to make sure it is valid, allow an option function call on the model to initialize
            new_model.save()
            return new_model
        else:
            value = select_value
            if value in EMPTY_VALUES:
                return None
            
            try:
                key = self.to_field_name or 'pk'
                value = self.queryset.get(**{key: value})
            except (ValueError, self.queryset.model.DoesNotExist):
                raise ValidationError(self.error_messages['invalid_choice'])
            
            return value
