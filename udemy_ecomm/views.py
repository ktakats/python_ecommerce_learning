from django.http import HttpResponse, JsonResponse

from django.shortcuts import render, redirect
from .forms import ContactForm


def home_page(request):
    context = {
        "title": "Hello World",
        "content": "Welcome to the home page",
        "premium_content": "Yay"
    }
    return render(request, 'home_page.html', context)



def about_page(request):
    return render(request, 'home_page.html', {"title": "About Page"})

def contact_page(request):
    contact_form=ContactForm(request.POST or None)
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
        if request.is_ajax():
            return JsonResponse({"message": "Thank you for your submission"})
    if contact_form.errors:
        errors = contact_form.errors.as_json()
        if request.is_ajax():
            return HttpResponse(errors, status=400, content_type='application/json')
    if request.method=="POST":
        print(request.POST)
    return render(request, 'contact/view.html', {"form": contact_form, "title": "Contact Page"})