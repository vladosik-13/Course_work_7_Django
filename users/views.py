from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, UpdateView, DetailView
)
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

# Регистрация пользователя
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'

# Вход пользователя
class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('home')

# Выход пользователя
class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('home')

# Профиль пользователя
class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user_profile'

    def get_object(self):
        return self.request.user

# Редактирование профиля пользователя
class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user
