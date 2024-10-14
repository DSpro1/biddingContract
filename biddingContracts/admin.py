from django.contrib import admin
from .models import Licitacao, Contrato, Fornecedor, NotaFiscal, AtaRegistroPreco
from .forms import formLicitacao
# Register your models here.
@admin.register(Licitacao)
class LicitacaoAdmin(admin.ModelAdmin):
    form = formLicitacao
    list_display = ("numProcess", "categoria", "assunto", "date",)
    search_fields = ["numProcess"]





#admin.site.register(Licitacao)
admin.site.register(Contrato)
admin.site.register(Fornecedor)
admin.site.register(NotaFiscal)
admin.site.register(AtaRegistroPreco)
