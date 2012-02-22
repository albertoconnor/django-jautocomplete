from django.shortcuts import render

from autocomplete_test.example.forms import TestForm

def test(request, template="test.html"):
    form = TestForm()
    return render(request,
                  template,
                  dict(form=form))