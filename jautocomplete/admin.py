from django.conf import settings
from django.contrib import admin
from django.db import models

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.html import escape
from django.utils.encoding import force_unicode

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect

from widgets import ForeignKeyAutocompleteInput

class AutocompleteModelAdmin(admin.ModelAdmin):
    def formfield_for_dbfield(self, db_field, **kwargs):
        # For ForeignKey use a special Autocomplete widget.
        if isinstance(db_field, models.ForeignKey) and hasattr(self, "autocomplete_fields") and db_field.name in self.autocomplete_fields:
            kwargs['widget'] = ForeignKeyAutocompleteInput(db_field.rel)
            # extra HTML to the end of the rendered output.
            if 'request' in kwargs.keys():
                kwargs.pop('request')
                                                        
            formfield = db_field.formfield(**kwargs)
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget = AutocompleteWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
            return formfield

        return super(AutocompleteModelAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        

class AutocompleteTargetModelAdmin(admin.ModelAdmin):        

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if request.POST.has_key("_continue"):
                self.message_user(request, msg + ' ' + _("You may edit it again below."))
                if request.POST.has_key("_popup"):
                        post_url_continue += "?_popup=%s" % request.POST.get('_popup')
                return HttpResponseRedirect(post_url_continue % pk_value)
        
        if request.POST.has_key("_popup"):
                #htturn response to Autocomplete PopUp
                if request.POST.has_key("_popup"):
                        return HttpResponse('<script type="text/javascript">opener.dismissAutocompletePopup(window, "%s", "%s");</script>' % (escape(pk_value), escape(obj)))
                                        
        elif request.POST.has_key("_addanother"):
                self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
                return HttpResponseRedirect(request.path)
        else:
                self.message_user(request, msg)

                # Figure out where to redirect. If the user has change permission,
                # redirect to the change-list page for this object. Otherwise,
                # redirect to the admin index.
                if self.has_change_permission(request, None):
                        post_url = '../'
                else:
                        post_url = '../../../'
                return HttpResponseRedirect(post_url)
                        
class AutocompleteWidgetWrapper(admin.widgets.RelatedFieldWidgetWrapper):
        def render(self, name, value, *args, **kwargs):
                rel_to = self.rel.to
                related_url = '../../../%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower())
                self.widget.choices = self.choices
                output = [self.widget.render(name, value, *args, **kwargs)]
                if rel_to in self.admin_site._registry: # If the related object has an admin interface:
                        # TODO: "id_" is hard-coded here. This should instead use the correct
                        # API to determine the ID dynamically.
                        output.append(u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAutocompletePopup(this);"> ' % \
                                (related_url, name))
                        output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
                return mark_safe(u''.join(output))