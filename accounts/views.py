from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import UserCreationForm, AssistentForm, ApotheekForm
from .models import User


def login_view(request):
    if request.method == "POST":
        email = request.POST['email-username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            print("OK")
            login(request, user)
            messages.success(request, 'Succesvol aangemeld')
            return redirect('home')  # Redirect to a success page.
        else:
            print("NIET OK")
            # Return an 'invalid login' error message.
            messages.error(request, 'Ongeldige gebruikersnaam of wachtwoord')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Succesvol afgemeld")
    return redirect('home')


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            role = user_form.cleaned_data.get('role')
            user.username = user.email
            user.save()
            if role == User.ASSISTENT:
                assistent_form = AssistentForm(request.POST)
                if assistent_form.is_valid():
                    assistent = assistent_form.save(commit=False)
                    assistent.user = user
                    assistent.save()
            elif role == User.APOTHEEK:
                apotheek_form = ApotheekForm(request.POST)
                if apotheek_form.is_valid():
                    apotheek = apotheek_form.save(commit=False)
                    apotheek.user = user
                    apotheek.save()
            return redirect('home')
    else:
        user_form = UserCreationForm()
        assistent_form = AssistentForm()
        apotheek_form = ApotheekForm()

    return render(request, 'accounts/register.html', {
        'user_form': user_form,
        'assistent_form': assistent_form,
        'apotheek_form': apotheek_form,
    })
