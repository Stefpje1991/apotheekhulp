from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from accounts.models import User


def admin_required(view_func):
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.ADMIN:
            return redirect('home')  # Redirect to a "not authorized" page or home
        return view_func(request, *args, **kwargs)
    return wrapper
