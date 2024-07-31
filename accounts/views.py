from django.contrib import messages, auth
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .decorators import admin_required

from .forms import UserCreationForm, AssistentForm, ApotheekForm, UserEditForm
from .models import User, Assistent, Apotheek


def login_view(request):
    if request.method == "POST":
        email = request.POST['email-username']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Succesvol aangemeld')
            return redirect('home')  # Redirect to a success page.
        else:
            # Return an 'invalid login' error message.
            messages.error(request, 'Ongeldige gebruikersnaam of wachtwoord')
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "Succesvol afgemeld")
    return redirect('home')


@admin_required
def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        assistent_form = ""
        apotheek_form = ""
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


@login_required(login_url='login')
def edit_userprofile(request):
    if request.method == 'POST':
        user = request.user
        if 'delete_profile_picture' in request.POST:
            user.profile_picture.delete(save=False)  # Delete the profile picture file
            user.profile_picture = None  # Set the profile picture field to None
            user.save()
            messages.success(request, "Profielfoto is verwijderd")
            return redirect('edit_userprofile')
        else:
            form = UserEditForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Gebruikersprofiel werd aangepast")
                return redirect('edit_userprofile')
    else:
        form = UserEditForm(instance=request.user)

    return render(request, 'accounts/userprofile.html', {'form': form})


@login_required(login_url='login')
def edit_companyprofile(request):
    user = request.user

    if user.role == 1:
        form_class = AssistentForm
        company_instance = Assistent.objects.get(user=user)  # Replace with correct query
    else:
        form_class = ApotheekForm
        company_instance = Apotheek.objects.get(user=user)  # Replace with correct query

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=company_instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Bedrijfsprofiel werd aangepast")
            return redirect('edit_companyprofile')
        else:
            print(form.errors)
    else:
        form = form_class(instance=company_instance)

        # Print field names and their values
    print("Form fields and values:")
    for field in form:
        field_name = field.name
        field_value = form.initial.get(field_name, None)  # Use cleaned_data to get the value
        print(f"Field Name: {field_name}, Value: {field_value}")

    return render(request, 'accounts/companyprofile.html', {'form': form})