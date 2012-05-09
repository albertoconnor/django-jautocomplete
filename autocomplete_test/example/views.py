from django.shortcuts import render

from autocomplete_test.example.forms import TestForm, ComboForm

forms = {
    "default": TestForm,
    "combo": ComboForm
}

def test(request, form_id="default", template="test.html"):
    if request.method == "POST":
        form = forms[form_id](request.POST)
        if form.is_valid():
            v = form.cleaned_data["value"]
    else:
        form = forms[form_id]()
    return render(request,
                  template,
                  dict(form=form))