from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm, AssistentForm


def register_assistent(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        assistent_form = AssistentForm(request.POST)
        if user_form.is_valid() and assistent_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.role = 1
            user.username = user.email
            user.save()

            assistent = assistent_form.save(commit=False)
            assistent.user = user
            assistent.save()

            messages.success(request, "Account werd aangemaakt")
            return redirect('home')  # Replace 'home' with your actual home page URL name
    else:
        user_form = UserForm()
        assistent_form = AssistentForm()

    return render(request, 'accounts/registerassistent.html', {
        'user_form': user_form,
        'assistent_form': assistent_form,
    })