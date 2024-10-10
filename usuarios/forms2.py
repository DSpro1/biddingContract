from django import forms
from biddingContracts.models import Secretaria
from django.contrib.auth import get_user_model
User = get_user_model()


from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Login",
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite seu login"
            }
        )
    )
    password = forms.CharField(
        label="Senha",
        required=True,
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite a sua senha"
            }
        )
    )
    
    
    
#Fomulário de Cadastro
class CadastroForms(forms.Form):
    nome_cadastro = forms.CharField(
        label="Digite um nome de usuário",
        required=True,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ex.: JoaoSilva"
            }
        )
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        max_length=100,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite um email válido"
            }
        )
    )
    senha = forms.CharField(
        label="Senha",
        required=True,
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite sua senha"
            }
        )
    )
    senha_confirme = forms.CharField(
        label="Confirmação de senha",
        required=True,
        max_length=20,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Digite sua senha mais uma vez"
            }
        )
    )

    def __init__(self, *args, **kwargs):
        self.mostrar_secretaria = kwargs.pop('mostrar_secretaria', False)
        super().__init__(*args, **kwargs)

        if self.mostrar_secretaria:
            self.fields['secretaria'] = forms.ModelChoiceField(
                label="Secretaria",
                required=True,
                queryset=Secretaria.objects.all(),
                widget=forms.Select(
                    attrs={
                        "class": "form-control"
                    }
                )
            )

    #Validação de Cadastro
    def clean_nome_cadastro(self):
        nome = self.cleaned_data.get("nome_cadastro")

        if nome:
            nome = nome.strip()
            if " " in nome:
                raise forms.ValidationError("Não é possivel inserir espaços dentro do campo Nome de Cadastro")
            else:
                return nome
            
    #Confirmação de senha
    def clean_senha_confirme(self):
        senha = self.cleaned_data.get("senha")
        senha_confirme = self.cleaned_data.get("senha_confirme")

        if senha and senha_confirme:
            if senha != senha_confirme:
                raise forms.ValidationError("Senhas não são iguais")
            else:
                return senha_confirme
            
            
            
class UpdateEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    