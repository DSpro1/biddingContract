from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from datetime import date

User  = get_user_model()


# Classe para o armazenamento dos dados excluídos
class RegistroExcluido(models.Model):
    modelo = models.CharField(max_length=100)
    dados_excluidos = models.JSONField() # Armazena os dados excluídos em formato JSON
    data_exclusao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, null=True, 
    )

    def __str__(self):
        return f"{self.modelo} excluido por {self.usuario} em {self.data_exclusao}"
    
    class Meta:
        verbose_name = "Registro Excluído"
        verbose_name_plural = "Registros Excluídos"
    

# Classe Para registrar o dia e hora separadaos 
class UsuarioExclusao(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    data_exclusão = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} excluiu um registro em  {self.data_exclusão}"

    class Meta:
        verbose_name = "Usuário que excluiu"
        verbose_name_plural = "Usuários que excluíram"


class Modalidade(models.TextChoices):
    CONCORRENCIA = 'concorrência', 'Concorrência'
    PREGAO = 'pregao', 'Pregão'
    LEILAO = 'leilao', 'Leilão'
    CONCURSO = 'concurso', 'Concurso'
    DIALOGO_COMPETITIVO = 'dialogo_competitivo', 'Diálogo Competitivo'

class Licitacao (models.Model):
    numProcess = models.CharField(max_length=7, unique=True, blank=False, null=False)
    categoria = models.CharField(max_length=150, choices=Modalidade.choices)
    assunto = models.CharField(max_length=200, verbose_name="Assunto",  null=False, blank=False)
    date = models.DateField()
    
    def __str__(self):
        return f"{self.numProcess}"

    class Meta:
        verbose_name = "licitação"
        verbose_name_plural = "licitações"

#Fornecedor
class Fornecedor(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do fornecedor", null=False, blank=False)
    cnpj = models.CharField(max_length=200, unique=True, verbose_name="Cadastro de Pessoa Jurídica", null=False, blank=False)
    endereco = models.CharField(max_length=200)
    num  = models.CharField(max_length=200)
    bairro  = models.CharField(max_length=200)
    cep = models.CharField(max_length=200)
    cidade = models.CharField(max_length=200)
    telefone = models.CharField(max_length=200)
    uf = models.CharField(max_length=2, null=True)

    def __str__(self):
        return f"{self.nome}"
    
    class Meta:
        verbose_name = "Fornecedor"
        verbose_name_plural = "fornecedores"

#Contrato
class Contrato(models.Model):
    numero = models.CharField(max_length=7, null=False, unique=True, blank=False)
    assuntoDetalhado = models.TextField(max_length=200, verbose_name="Detalhe do contrato", null=False, blank=False)
    dataInicial = models.DateField()
    dataFinal = models.DateField()
    valor = models.FloatField(null=False)
    licitacao_fk= models.ForeignKey("Licitacao", on_delete=models.CASCADE)
    fornecedor_fk = models.ForeignKey("Fornecedor", on_delete=models.CASCADE)
    secretaria_fk = models.ManyToManyField("Secretaria", related_name="Contratos") # Para poder acessar de secretarias os contratos relacionados

    def __str__(self):
        return f"{self.numero}"
    

    def is_vencido(self):
        # Verifica se a data final do contrato já passou
        return self.dataFinal < timezone.now().date()
    
    def delete(self, usuario=None, using=None, keep_parents=False):
    
        print("Método delete chamado")
        try:
            # Armazenar os dados a serem excluídos
            dados_excluidos = {}
            for field in self._meta.get_fields():
                if not field.is_relation:
                    value = getattr(self, field.name)
                    if isinstance(value, date):
                        value = value.isoformat()  # Formato YYYY-MM-DD
                    dados_excluidos[field.name] = value
            
            # Criar o registro da exclusão no modelo RegistroExcluido
            RegistroExcluido.objects.create(
                modelo=self.__class__.__name__,
                dados_excluidos=dados_excluidos,
                usuario=usuario  # Passar o usuário que fez a exclusão
            )
            print("Registro Excluido criado com sucesso!")
        except Exception as e:
            print(f"Erro ao registrar dados excluídos: {e}") 

        # Chama o método de exclusão do pai
        super().delete(using, keep_parents)
    
#Secretaria
class Secretaria(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da secretaria", null=False, blank=False)
    programa = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f"{self.nome, self.programa}"
    
    class Meta:
        verbose_name = "Secretaria"
        verbose_name_plural = "Secretarias"


    def delete(self, usuario=None, using=None, keep_parents=False):
    
        print("Método delete chamado")
        try:
            # Armazenar os dados a serem excluídos
            dados_excluidos = {}
            for field in self._meta.get_fields():
                if not field.is_relation:
                    value = getattr(self, field.name)
                    if isinstance(value, date):
                        value = value.isoformat()  # Formato YYYY-MM-DD
                    dados_excluidos[field.name] = value
            
            # Criar o registro da exclusão no modelo RegistroExcluido
            RegistroExcluido.objects.create(
                modelo=self.__class__.__name__,
                dados_excluidos=dados_excluidos,
                usuario=usuario  # Passar o usuário que fez a exclusão
            )
            print("Registro Excluido criado com sucesso!")
        except Exception as e:
            print(f"Erro ao registrar dados excluídos: {e}") 

        # Chama o método de exclusão do pai
        super().delete(using, keep_parents)

class Tipo(models.TextChoices):
    PRESTACAO_SERVICO = "prestacao_servico", "Prestação de Serviço"
    AQUISICAO_BENS = "aquisicao_bens", "Aquisicao de Bens"

class NotaFiscal(models.Model):
    num = models.IntegerField()
    serie = models.CharField(max_length=3)
    valor = models.FloatField()
    tipo = models.CharField(max_length=50, choices=Tipo.choices)
    dataEmissao = models.DateField()
    contrato_fk = models.ForeignKey("Contrato", blank=True, null=True, on_delete=models.CASCADE)
    fornecedor_fk = models.ForeignKey("Fornecedor", on_delete=models.CASCADE)
    ataregistropreco_fk = models.ForeignKey('AtaRegistroPreco', blank=True, null=True, on_delete=models.CASCADE)

        
    class Meta:
        verbose_name_plural = "Notas Fiscais"

    def __str__(self):
        return f"{self.tipo}"
    
    def delete(self, usuario=None, using=None, keep_parents=False):
    
        print("Método delete chamado")
        try:
            # Armazenar os dados a serem excluídos
            dados_excluidos = {}
            for field in self._meta.get_fields():
                if not field.is_relation:
                    value = getattr(self, field.name)
                    if isinstance(value, date):
                        value = value.isoformat()  # Formato YYYY-MM-DD
                    dados_excluidos[field.name] = value
            
            # Criar o registro da exclusão no modelo RegistroExcluido
            RegistroExcluido.objects.create(
                modelo=self.__class__.__name__,
                dados_excluidos=dados_excluidos,
                usuario=usuario  # Passar o usuário que fez a exclusão
            )
            print("Registro Excluido criado com sucesso!")
        except Exception as e:
            print(f"Erro ao registrar dados excluídos: {e}") 

        # Chama o método de exclusão do pai
        super().delete(using, keep_parents)




class AtaRegistroPreco(models.Model):
    numero = models.CharField(max_length=7, null=False, blank=False)
    assuntoDetalhado = models.TextField(max_length=200, verbose_name="Detalhe do contrato", null=False, blank=False)
    dataInicial = models.DateField()
    dataFinal = models.DateField()
    valor = models.FloatField(null=False)
    licitacao_fk= models.ForeignKey("Licitacao", on_delete=models.CASCADE)
    fornecedor_fk = models.ForeignKey("Fornecedor", on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.numero}'
    
    class Meta:
        verbose_name_plural = 'Atas de Registros de Preços'

    def delete(self, usuario=None, using=None, keep_parents=False):
    
        print("Método delete chamado")
        try:
            # Armazenar os dados a serem excluídos
            dados_excluidos = {}
            for field in self._meta.get_fields():
                if not field.is_relation:
                    value = getattr(self, field.name)
                    if isinstance(value, date):
                        value = value.isoformat()  # Formato YYYY-MM-DD
                    dados_excluidos[field.name] = value
            
            # Criar o registro da exclusão no modelo RegistroExcluido
            RegistroExcluido.objects.create(
                modelo=self.__class__.__name__,
                dados_excluidos=dados_excluidos,
                usuario=usuario  # Passar o usuário que fez a exclusão
            )
            print("Registro Excluido criado com sucesso!")
        except Exception as e:
            print(f"Erro ao registrar dados excluídos: {e}") 

        # Chama o método de exclusão do pai
        super().delete(using, keep_parents)

    
    
    
