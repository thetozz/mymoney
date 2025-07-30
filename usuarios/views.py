from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView


class RegistroView(CreateView):
    form_class = UserCreationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')

    def form_valid(self, form):
        messages.success(
            self.request, 'Conta criada com sucesso! Faça login para continuar.')
        return super().form_valid(form)


def home_view(request):
    """Página inicial - redireciona para dashboard se logado"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return redirect('usuarios:login')
