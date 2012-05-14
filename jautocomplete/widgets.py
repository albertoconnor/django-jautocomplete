from django.conf import settings
from django import forms
from django.forms.util import flatatt
from django.db import models
from django.template.loader import render_to_string

from django.utils.safestring import mark_safe

class ComboInput(forms.widgets.Select):
    def value_from_datadict(self, data, files, name):
        return (data.get(name, None), data.get("%s_new" % name, None))
        
    def render(self, name, value, attrs=None):
        rendered = super(ComboInput, self).render(name, value, attrs)
        return rendered + mark_safe('or new value: <input type="text" id="id_%s_new" name="%s_new" value=""/>' % (name,name))
        
class ComboAutocompleteInput(ComboInput):
    
    class Media:
        css = {
                'all': ('%scss/jquery.autocomplete.css' % settings.STATIC_URL,)
        }
        js = (
                '%sjs/lib/jquery.autocomplete.js' % settings.STATIC_URL,
        )
    
    def render(self, name, value, attrs=None):
        rendered = super(ComboAutocompleteInput, self).render(name, value, attrs)
        if value is None or value == (u'', u''): # Handle the blank case correctly
            value = ""
        if isinstance(value, tuple):
            value = value[0] # handle the form isn't valid case
        try: # Handle the pre existing value case correctly
            pk = int(value)
            # Depending on internal details, this may not be the best way, and doesn't correctly support to_field_name
            try:
                value_obj = self.choices.queryset.model.objects.get(pk=pk)
                value = unicode(value_obj)
            except self.choices.queryset.model.DoesNotExist:
                value = ''
        except ValueError:
            pass
        return render_to_string("jautocomplete/_comboautocompleteinput.html", dict(name=name,
                                                                                   value=value,
                                                                                   attr=flatatt(attrs),
                                                                                   rendered=rendered))

class ForeignKeyAutocompleteInput(forms.widgets.Select):
    """
    A pair of widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.  One is a hidden widget with the real value, the
    other is a textbox the autocomplete will take place on.
    """
    class Media:
        css = {
                'all': ('%scss/jquery.autocomplete.css' % settings.STATIC_URL,)
        }
        js = (
                '%sjs/lib/jquery.autocomplete.js' % settings.STATIC_URL,
                '%sjs/autocomplete.popup.js ' % settings.STATIC_URL
        )

    def text_field_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        
        return unicode(obj)

    def __init__(self,
                 rel,
                 attrs=None):
        """
        rel - the relation for the foreign key.
        """
        self.rel = rel
        super(ForeignKeyAutocompleteInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(ForeignKeyAutocompleteInput, self).render(name, value, attrs)
        if value:
            text_field_value = self.text_field_value(value)
        else:
            text_field_value = u''
        return rendered + mark_safe(javascript_template % {
                            'MEDIA_URL': settings.MEDIA_URL,
                            'model_name': self.rel.to._meta.module_name,
                            'app_label': self.rel.to._meta.app_label,
                            'text_field_value': text_field_value,
                            'text_field_size': 40,
                            'name': name,
                            'value': value,
                })
        
class SelectAutocompleteInput(forms.widgets.Select):
    """
    A pair of widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.  One is a hidden widget with the real value, the
    other is a textbox the autocomplete will take place on.
    """
    class Media:
        css = {
                'all': ('%scss/jquery.autocomplete.css' % settings.STATIC_URL,)
        }
        js = (
                '%sjs/lib/jquery.autocomplete.js' % settings.STATIC_URL,
                '%sjs/autocomplete.popup.js ' % settings.STATIC_URL
        )

    #def text_field_value(self, value):
    #    key = self.rel.get_related_field().name
    #    obj = self.rel.to._default_manager.get(**{key: value})
        
    #    return unicode(obj)

    def __init__(self, attrs=None):
        super(SelectAutocompleteInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(SelectAutocompleteInput, self).render(name, value, attrs)
        # Need to translate the value into a readable value...
        if value:
            text_field_value = value
            #text_field_value = self.text_field_value(value)
        else:
            text_field_value = u''
        return rendered + mark_safe(javascript_template % {
                            'MEDIA_URL': settings.STATIC_URL,
                            'text_field_value': text_field_value,
                            'text_field_size': 40,
                            'name': name,
                            'value': value,
                })


javascript_template = u'''
<input type="text" id="lookup_%(name)s" value="%(text_field_value)s" size="%(text_field_size)s" style="display: none;"/>
<script type="text/javascript">

$(document).ready(function(){
    // Javascript is required to show the autocomplete field and hide the select field.
    $("#id_%(name)s").hide();
    $("#lookup_%(name)s").show();

    function liFormat_%(name)s (row, i, num) {
            var result = row[0] ;
            return result;
    }
    
    var %(name)s_data = Array();
    var %(name)s_id_map = {};
    
    function load_autocomplete_data_from_select() {
        %(name)s_data = Array();
        %(name)s_id_map = {};
        $("#id_%(name)s option").each(function(d) {
            var value = $(this).html() 
            %(name)s_data.push(value);
            %(name)s_id_map[value] = $(this).val();
        })
        
        $("#lookup_%(name)s").autocomplete(%(name)s_data, {
            delay:10,
            minChars:1,
            matchSubset:1,
            autoFill:false,
            matchContains:1,
            cacheLength:10,
            selectFirst:true,
            formatItem:liFormat_%(name)s,
            maxItemsToShow:10
        }); 
    }
    
    load_autocomplete_data_from_select(); // Inital load
    
    // Changing the autocomplete field needs to change the hidden select field
    $("#lookup_%(name)s").change(function() {
        new_value = %(name)s_id_map[$(this).val()];
        if (new_value == undefined) {
            new_value = ""
        }
        $("#id_%(name)s").val(new_value); 
    })
    
    // It is possible to "change" the autocomplete text field and have the change
    // event not happen.  This double checks right before we submit.
    $("form").submit(function() {
        $("#lookup_%(name)s").change(); // Just to make sure
    })
    
    // When the add feature is used, it only knows how to change the select field
    // so the autocomplete field needs to be updated too.
    $("#id_%(name)s").change(function () {
        $("#lookup_%(name)s").val($(this).find("option:selected").html());
        load_autocomplete_data_from_select(); // Could be a new value from an add
    })    
});
</script>'''