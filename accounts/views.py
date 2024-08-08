from django.contrib import messages, auth
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .decorators import role_required
from .forms import UserCreationForm, AssistentForm, ApotheekForm, UserEditForm, ChangePasswordForm
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
@role_required(1, 2)
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

    return render(request, 'accounts/companyprofile.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            user = request.user
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Important, to keep the user logged in
            messages.success(request, 'Je wachtwoord werd succesvol aangepast!')
            return redirect('home')  # Redirect to a success page or profile page
    else:
        form = ChangePasswordForm()

    return render(request, 'accounts/change_password.html', {'form': form})


@login_required(login_url='login')
@role_required(3)
def overview_assistenten(request):
    assistenten = Assistent.objects.all().order_by('user__last_name')
    context = {
        'assistenten': assistenten
    }
    return render(request, 'accounts/admin/overview_assistenten_admin.html', context)


@login_required(login_url='login')
@role_required(3)
def overview_apotheken(request):
    apotheken = Apotheek.objects.all().order_by('user__last_name')
    context = {
        'apotheken': apotheken
    }
    return render(request, 'accounts/admin/overview_apotheken_admin.html', context)


@login_required(login_url='login')
@role_required(3)
def edit_userprofile_admin(request, user_id):
    # Fetch the Assistent object and its associated User
    assistent_id = 0
    apotheek_id = 0
    gebruiker = get_object_or_404(User, id=user_id)
    if gebruiker.role == 1:
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id

    else:
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id

    user_id = gebruiker.id

    if request.method == 'POST':
        # Handle deletion of profile picture
        if 'delete_profile_picture' in request.POST:
            if gebruiker.profile_picture:
                gebruiker.profile_picture.delete(save=False)  # Delete the profile picture file
                gebruiker.profile_picture = None  # Set the profile picture field to None
                gebruiker.save()
                messages.success(request, "Profielfoto is verwijderd")
            return redirect('edit_userprofile_admin', user_id=user_id)

        # Handle form submission for editing user details
        form = UserEditForm(request.POST, request.FILES, instance=gebruiker)
        if form.is_valid():
            form.save()
            messages.success(request, "Gebruikersprofiel werd aangepast")
            return redirect('edit_userprofile_admin', user_id=user_id)
    else:
        form = UserEditForm(instance=gebruiker)
        context = {
            'form': form,
            'assistent_id': assistent_id,
            'apotheek_id': apotheek_id,
            'gebruiker': gebruiker,
            'user_id': user_id,
        }
        return render(request, 'accounts/admin/userprofile_admin.html', context=context)


@login_required(login_url='login')
@role_required(3)
def edit_companyprofile_assistent_admin(request, assistent_id):
    assistent = get_object_or_404(Assistent, id=assistent_id)
    gebruiker = assistent.user
    user_id = gebruiker.id

    if request.method == 'POST':
        form = AssistentForm(request.POST, request.FILES, instance=assistent)
        if form.is_valid():
            form.save()
            messages.success(request, "Bedrijfsprofiel werd aangepast")
            return redirect('edit_companyprofile_assistent_admin', assistent_id=assistent_id)
        else:
            print(form.errors)
    else:
        form = AssistentForm(instance=assistent)

    context = {
        'gebruiker': gebruiker,
        'user_id': user_id,
        'assistent_id': assistent_id,
        'form': form
    }

    return render(request, 'accounts/admin/companyprofile_assistent_admin.html', context)


@login_required(login_url='login')
@role_required(3)
def edit_companyprofile_apotheek_admin(request, apotheek_id):
    apotheek = get_object_or_404(Apotheek, id=apotheek_id)
    gebruiker = apotheek.user
    user_id = gebruiker.id

    if request.method == 'POST':
        form = ApotheekForm(request.POST, request.FILES, instance=apotheek)
        if form.is_valid():
            form.save()
            messages.success(request, "Bedrijfsprofiel werd aangepast")
            return redirect('edit_companyprofile_apotheek_admin', apotheek_id=apotheek_id)
        else:
            print(form.errors)
    else:
        form = ApotheekForm(instance=apotheek)

    context = {
        'gebruiker': gebruiker,
        'user_id': user_id,
        'apotheek_id': apotheek_id,
        'form': form
    }

    return render(request, 'accounts/admin/companyprofile_apotheek_admin.html', context)


@login_required
@role_required(3)
def change_password_user(request, user_id):
    assistent_id = 0
    apotheek_id = 0
    gebruiker = get_object_or_404(User, id=user_id)
    if gebruiker.role == 1:
        assistent = get_object_or_404(Assistent, user=gebruiker)
        assistent_id = assistent.id
    elif gebruiker. role == 2:
        apotheek = get_object_or_404(Apotheek, user=gebruiker)
        apotheek_id = apotheek.id
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            gebruiker.set_password(new_password)
            gebruiker.save()

            messages.success(request, 'Wachtwoord werd succesvol aangepast!')
            if gebruiker.role == 1:
                return redirect('overview_assistenten')  # Redirect to a success page or profile page
            elif gebruiker.role == 2:
                return redirect('overview_apotheken')
    else:
        form = ChangePasswordForm()
        context = {
            'gebruiker': gebruiker,
            'user_id': user_id,
            'assistent_id': assistent_id,
            'apotheek_id': apotheek_id,
            'form': form
        }

        return render(request, 'accounts/admin/change_password_admin.html', context)


@login_required
@role_required(3)
def add_nieuwe_assistent_admin(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        assistent_form = AssistentForm(request.POST)
        print(request.POST)
        if user_form.is_valid() and assistent_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # Use password1 for password validation
            user.username = user.email
            user.role = 1
            user.save()

            assistent = assistent_form.save(commit=False)
            assistent.user = user
            assistent.save()
            messages.success(request, 'Assistent werd succesvol aangemaakt')
            return redirect('overview_assistenten')
    else:
        user_form = UserCreationForm()
        assistent_form = AssistentForm()

    return render(request, 'accounts/admin/nieuwe_assistent_admin.html', {
        'user_form': user_form,
        'assistent_form': assistent_form,
    })


@login_required
@role_required(3)
def add_nieuwe_apotheek_admin(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        apotheek_form = ApotheekForm(request.POST)

        if user_form.is_valid() and apotheek_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])  # Use password1 for password validation
            user.username = user.email
            user.role = 1
            user.save()

            assistent = apotheek_form.save(commit=False)
            assistent.user = user
            assistent.save()
            messages.success(request, 'Apotheek werd succesvol aangemaakt')
            return redirect('overview_assistenten')
    else:
        user_form = UserCreationForm()
        apotheek_form = ApotheekForm()

    return render(request, 'accounts/admin/nieuwe_apotheek_admin.html', {
        'user_form': user_form,
        'apotheek_form': apotheek_form,
    })
