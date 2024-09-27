from django.shortcuts import render, redirect
from django. urls import reverse_lazy
from usuarios.forms2 import  CadastroForms, CustomLoginForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages, auth


def login(request):
    form = CustomLoginForm()

    if request.method == 'POST':
        form = CustomLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            usuario = authenticate(
                request,
                username=username,
                password=password
            )
            if usuario is not None and usuario.is_active:
                messages.success(request, 'Login efetuado com sucesso!')
                auth_login(request, usuario)
                return reverse_lazy('index')  # Redireciona para a página inicial após login bem-sucedido
            else:
                messages.error(request, 'Login inválido! Dados incorretos ou conta não ativada.')
                return reverse_lazy('usuarios:login')  # Redireciona para a view de login em caso de erro
    else:
        messages.info(request, 'Por favor, faça login para acessar.')
    
    return render(request, "registration/login.html", {"form": form})


def cadastro(request):
    form = CadastroForms()

    if request.method == 'POST':
        form = CadastroForms(request.POST)

        if form.is_valid():
            
            nome = form["nome_cadastro"].value()
            email = form["email"].value()
            senha = form["senha"].value()
            
            if User.objects.filter(username=nome).exists():
                return redirect('login')

            usuario = User.objects.create_user(
                username=nome,
                email=email,
                password=senha
            )
            usuario.is_active = False
            usuario.save()
            aviso = 'Cadastro efetuado com sucesso!'
            aviso2 = 'Entre em contato com o administrador solicitando a liberação do sistema!'
            messages.success(request, aviso)
            messages.warning(request, aviso2)
            return redirect('login')

    return render(request, "registration/cadastro.html", {"form": form})


def logout(request):
    auth.logout(request)
    messages.success(request, "Deslogado com sucesso!")
    return reverse_lazy('login')


