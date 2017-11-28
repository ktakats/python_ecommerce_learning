from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.shortcuts import render, redirect
from .forms import ContactForm, LoginForm, RegisterForm

User=get_user_model()

def home_page(request):
    context = {
        "title": "Hello World",
        "content": "Welcome to the home page",
        "premium_content": "Yay"
    }
    return render(request, 'home_page.html', context)

def login_page(request):
    form=LoginForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
        username=form.cleaned_data.get("username")
        password=form.cleaned_data.get("password")
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            form=LoginForm()
            return redirect("/")
        else:
            print("Error")
    return render(request, "auth/login.html", {"form": form})

def register_page(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        data=form.cleaned_data
        username=data['username']
        email=data['email']
        password=data['password']
        new_user = User.objects.create_user(username, email, password)
        form = RegisterForm()
    return render(request, "auth/register.html", {"form": form})

def about_page(request):
    return render(request, 'home_page.html', {"title": "About Page"})

def contact_page(request):
    contact_form=ContactForm(request.POST or None)
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
    if request.method=="POST":
        print(request.POST)
    return render(request, 'contact/view.html', {"form": contact_form, "title": "Contact Page"})