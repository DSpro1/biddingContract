from django.shortcuts import render
#from django.http import HttpResponseRedirect
#from  .forms import formLicitacao, formFornecedor, formContrato
from django.urls import reverse
from .models import Contrato, NotaFiscal
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

def listContratos(request):
    contratos = Contrato.objects.all()
    context = {"contratos": contratos}
    return render(request, "contratos.html", context)

def contratosRelatorio(request, id_contrato):
    contrato = Contrato.objects.get(numero=id_contrato)
    notasFiscais = NotaFiscal.objects.filter(contrato_fk = id_contrato)
    saldoAtual = contrato.valor
    #tipo datetime.datetime
    hoje = datetime.today()
    # convertendo para o tipo datetime.date
    hoje = hoje.date()
    # tipo datetime.date
    dataFinalContrato = contrato.dataFinal  
    prazoRestante = relativedelta(dataFinalContrato, hoje)
    mensagem = verifica_prazo_validade_contrato(prazoRestante, dataFinalContrato, hoje)

    for notas in notasFiscais:
        if notas.contrato_fk.numero == contrato.numero:
            saldoAtual -= notas.valor
    context = {
        "notasfiscais": notasFiscais,
        "saldoAtual": saldoAtual,
        "vigencia": mensagem
        }
    return render(request, "contratos_relatorio.html", context)

def verifica_prazo_validade_contrato(prazoRestante, dataFinal, hoje):
    mensagem = " "
    if dataFinal >= hoje:
        mensagem = f"O contrato é válido por mais {prazoRestante.years} anos, {prazoRestante.months} meses e {prazoRestante.days} dias."
        return mensagem
    else:
        mensagem =  "O prazo de validade do contrato já expirou."
    return mensagem
# INDEX
def index(request):
    return render(request, 'index.html')