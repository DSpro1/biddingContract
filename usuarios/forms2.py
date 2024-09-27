from django import forms


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
                "placeholder": "Ex.: JoãoSilva"
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
                "placeholder": "joaosilva@xpto.com.br"
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