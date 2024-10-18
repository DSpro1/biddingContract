from django.http import JsonResponse
from django.shortcuts import render
from biddingContracts.models import Contrato, NotaFiscal
from django.db.models import Sum
from datetime import datetime
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth, ExtractYear


def retorna_total_valores(request):
    contratos = Contrato.objects.aggregate(valor_total=Sum('valor'))['valor_total']
    valor_notas = NotaFiscal.objects.aggregate(valor_total=Sum('valor'))['valor_total']
    
    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
    
    # Calculate data for chart 1: Contratos
    contratos_por_mes = Contrato.objects.annotate(
        mes=TruncMonth('dataInicial'),
        ano=ExtractYear('dataInicial')
    ).values('mes', 'ano').annotate(valor_total=Sum('valor')).order_by('ano', 'mes')

    data_contratos = [contrato['valor_total'] for contrato in contratos_por_mes]
    labels_contratos = [f"{meses[contrato['mes'].month - 1]} {contrato['ano']}" for contrato in contratos_por_mes]
    
    # Calculate data for chart 2: Notas Fiscais
    notas_por_mes = NotaFiscal.objects.annotate(
        mes=TruncMonth('data'),
        ano=ExtractYear('data')
    ).values('mes', 'ano').annotate(valor_total=Sum('valor')).order_by('ano', 'mes')

    data_notas = [nota['valor_total'] for nota in notas_por_mes]
    labels_notas = [f"{meses[nota['mes'].month - 1]} {nota['ano']}" for nota in notas_por_mes]
    
    context = {
        'contratos': contratos,
        'valor_notas_total': valor_notas,
        'data_contratos': data_contratos,
        'labels_contratos': labels_contratos,
        'data_notas': data_notas,
        'labels_notas': labels_notas
    }
    return render(request, "dash/dash.html", context)


def contrato_valor_por_mes(request):
    contratos = Contrato.objects.annotate(
        mes=TruncMonth('dataInicial'),
        ano=ExtractYear('dataInicial')
    ).values('mes', 'ano').annotate(
        valor_total=Sum('valor')
    ).order_by('ano', 'mes')

    meses = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']

    data = []
    labels = []
    for contrato in contratos:
        data.append(contrato['valor_total'])
        labels.append(f"{meses[contrato['mes'].month-1]} {contrato['ano']}")

    #data_json = {'data': data, 'labels': labels}

    # return JsonResponse(data_json)
    return render(request, 'dash/dash.html', {'data': data, 'labels': labels})



def renderizar(request):
    return render(request, "dash/dash.html")