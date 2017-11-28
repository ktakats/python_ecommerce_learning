from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model
from django.utils.http import is_safe_url
from .forms import LoginForm, RegisterForm

User = get_user_model()
# Create your views here.
def login_page(request):
    form=LoginForm(request.POST or None)
    next_ = request.GET.get("next")
    next_post = request.POST.get("next")
    redirect_path = next_ or next_post or None
    if form.is_valid():
        username=form.cleaned_data.get("username")
        password=form.cleaned_data.get("password")
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            form=LoginForm()
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        else:
            print("Error")
    return render(request, "accounts/login.html", {"form": form})

def register_page(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        data=form.cleaned_data
        username=data['username']
        email=data['email']
        password=data['password']
        new_user = User.objects.create_user(username, email, password)
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})