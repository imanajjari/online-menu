from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import OwnerSignUpForm, OwnerLoginForm


class OwnerLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = OwnerLoginForm
    redirect_authenticated_user = True


class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = OwnerSignUpForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "حساب کاربری با موفقیت ایجاد شد.")
        return redirect(self.success_url)
