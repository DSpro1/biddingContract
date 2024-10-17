from django.db.models.query import QuerySet
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from datetime import datetime, timedelta
from django.db.models import Q
from  biddingContracts.forms import formLicitacao, formFornecedor,NotaFiscalEditForm, formContrato, formARP, NotaFiscalForm, formSecretaria
from django.urls import reverse, reverse_lazy
from .models import Contrato, NotaFiscal, Fornecedor, Licitacao, AtaRegistroPreco, Secretaria, RegistroExcluido
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages

import tempfile
from django.utils import timezone
#import weasyprint
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Sum



@login_required
@permission_required("biddingContracts.add_contrato") # Permissão de criar contratos
def cadContrato(request, fornecedor_id):
    if request.method == "POST":
        form = formContrato(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Contrato criado com sucesso!")
            return HttpResponseRedirect(reverse("biddingContracts:contratos"))
        else:
            print(f"Deu errado!{form.errors}")
    else:
        form = formContrato()

    return render(request, "contratos/contrato_new.html", {"form": form, "fornecedor_id": fornecedor_id})
    


# class ListContractsView(LoginRequiredMixin, ListView):
    
#     # fluxo 2-> segunda requisição, ou seja, quando ele vem da tela de cadastro de fornecedor.
#     if fornecedor_id!=0:
#         #consulta o fornecedor vindo do banco através do ID e cria um objeto com os dados retornado da tabela fornecedor
#         fornecedor = Fornecedor.objects.get(id = fornecedor_id)
        
#         form = formContrato()
#         context={'form':form, 'fornecedor_id':fornecedor.id}
#         return render(request, 'contrato_new.html', context)
    
#     # fluxo 1 -> primeira requisição get
#     else:
#         form = formContrato()
#         context={'form':form,'fornecedor_id':fornecedor_id}
#         return render(request, "contrato_new.html", context)
    

class ListContractsView(PermissionRequiredMixin, ListView):
    """
    Classe destinada a listar os contratos criados
    """
    model = Contrato
    template_name = "contratos/contratos.html"
    context_object_name = "contratos"
    permission_required = ["biddingContracts.view_contrato"]

    # Adicionando filtros ao object_list através do get_queryset
    def get_queryset(self):
        today = datetime.now().date() # Data de hoje
        txt_contratos = self.request.GET.get("contratos")
        txt_assunto = self.request.GET.get("assunto")
        txt_fornecedor = self.request.GET.get("fornecedor")
        txt_licitacao = self.request.GET.get("licitacao")
        filter_expired = self.request.GET.get('search') == 'on'
        valor = self.request.GET.get("valor")

        if valor == "0":
            return Contrato.objects.filter(valor=0)
        if self.kwargs.get("zerados"):

            return Contrato.objects.filter(valor=0)

        
        # Filtro de contratos vencidos
        if filter_expired:
            return Contrato.objects.filter(dataFinal__lt=timezone.now().date())
        elif not filter_expired:
            return Contrato.objects.all()

        if txt_fornecedor:
            queryset = Contrato.objects.filter(fornecedor_fk__nome__icontains=txt_fornecedor)
            return queryset
        elif txt_licitacao:
            queryset = Contrato.objects.filter(licitacao_fk__numProcess__icontains=txt_licitacao)
            return queryset
        elif txt_contratos:
            queryset = Contrato.objects.filter(numero__icontains=txt_contratos)
            return queryset
        elif txt_assunto:
            queryset = Contrato.objects.filter(assuntoDetalhado__icontains=txt_assunto)
            return queryset
        else:
            queryset = Contrato.objects.all()
        return queryset
    
    
    
     # Adicionando o cálculo de vencimento ao contexto
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        contratos = context['contratos'] = self.get_queryset()
        today = timezone.now().date()  # Obtém a data atual

        # Adiciona um atributo 'vencido' a cada contrato
        for contrato in contratos:
            contrato.vencido = today > contrato.dataFinal  # Verifica se o contrato já venceu

        return context

def contrato_zerado(request):
    zerado = Contrato.objects.filter(valor__lte=0)
    context = {
        "zerados": zerado
    }
    return render(request, "contratos/contratos_zerados.html", context)

# View que atualiza os contratos
class ContractsUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Classe destinada a atualizar os contratos já criados
    """
    model = Contrato
    template_name = "contratos/edit_contratos.html"
    form_class = formContrato
    context_object_name = "contrato"
    permission_required = ["biddingContracts.change_contrato"]

    def form_valid(self, form):
        messages.success(self.request, 'Contrato editado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar Contrato. Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})
    
    def get_success_url(self):
        return reverse_lazy("biddingContracts:contratos")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fornecedores'] = Fornecedor.objects.all()
        return context


@login_required
def contratosRelatorio(request, id_contrato):
    contrato = Contrato.objects.get(id=id_contrato)
    notasFiscais = NotaFiscal.objects.filter(contrato_fk = id_contrato)
    saldoAtual = contrato.valor
    #tipo datetime.date
    hoje = datetime.today().date()
    
    # tipo datetime.date
    dataFinalContrato = contrato.dataFinal  
    prazoRestante = relativedelta(dataFinalContrato, hoje)
    
    mensagem = verifica_prazo_validade(prazoRestante, dataFinalContrato, hoje)

    for notas in notasFiscais:
        if notas.contrato_fk.numero == contrato.numero:
            saldoAtual -= notas.valor
    context = {
        "notasfiscais": notasFiscais,
        "saldoAtual": saldoAtual,
        "vigencia": mensagem,
        "hoje": hoje,
        "dataFinal": dataFinalContrato,
        "chave":True
        }
    return render(request, "contratos/contratos_relatorio.html", context)


def verifica_prazo_validade(prazoRestante, dataFinal,  hoje):
    mensagem = ""
    if dataFinal > hoje:
        mensagem = f"O contrato é válido por mais {prazoRestante.years} anos, {prazoRestante.months} meses e {prazoRestante.days} dias."
        return mensagem
    elif dataFinal == hoje:
        mensagem = f"O contrato é válido até hoje dia: {dataFinal.strftime('%d/%m/%y')}"
        return mensagem
    elif dataFinal < hoje:
        mensagem =  f"O prazo de validade do contrato já expirou."
    return mensagem


def verifica_prazo_validade_arp(prazoRestante, dataFinal, hoje):
    # return verifica_prazo_validade(prazoRestante, dataFinal, hoje, tipo="ARP")
    mensagem = ""
    if dataFinal > hoje:
        mensagem = f"Esta ARP é válida por mais {prazoRestante.years} anos, {prazoRestante.months} meses e {prazoRestante.days} dias."
        return mensagem
    elif dataFinal == hoje:
        mensagem = f"Esta ARP é válido até hoje dia: {dataFinal.strftime('%d/%m/%y')}"
        return mensagem
    elif dataFinal < hoje:
        #Aqui eu vi uma utilidade de ser armazenado no banco de dados o valor atual da ARP para quando 
        # for cadastrar o contrato já inserir o valor automaticamente para evitar possíveis erros do 
        # usuário de digitar um valor diferente do valor atual do contrato.
        mensagem =  "O prazo de validade desta ARP expirou, cadastre-a como contrato usando o saldo atual, clique aqui:" 
        
    return mensagem


# View que deleta os contratos
class ContractDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Contrato
    template_name = "contratos/contratos_delete.html"
    context_object_name = "contrato"
    permission_required = ["biddingContracts.delete_contrato"]

    def form_valid(self, form):
        contrato = self.get_object()
        fornecedor = contrato.fornecedor_fk
        licitacao = contrato.licitacao_fk

        # Verifica se existem outros contratos relacionados ao mesmo fornecedor ou à mesma licitação
        outro_contrato_fornecedor = Contrato.objects.filter(fornecedor_fk=fornecedor).exclude(pk=contrato.pk).exists()
        outro_contrato_licitacao = Contrato.objects.filter(licitacao_fk=licitacao).exclude(pk=contrato.pk).exists()

        # Só excluir o contrato se NÃO houver outros contratos relacionados ao mesmo fornecedor e à mesma licitação
        if not outro_contrato_fornecedor and not outro_contrato_licitacao:
            self.object.delete(usuario=self.request.user)
            #contrato.delete() # O método de excluir já é chamado na linha de cima
            messages.success(self.request, 'Contrato excluído com sucesso!')
            return redirect(self.get_success_url())
        else:
            contrato.valor = 0
            contrato.save()
            messages.error(self.request, 'Não é possível excluir o contrato, pois o fornecedor ou a licitação estão relacionados a outros contratos. Nesse caso o contrato foi zerado')
            return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("biddingContracts:contratos")


# INDEX
@login_required
def index(request):
    if request.user.is_authenticated:
        
        contratos = Contrato.objects.all()
        licitacoes = Licitacao.objects.all()
        notas_fiscais = NotaFiscal.objects.all()
        arp = AtaRegistroPreco.objects.all()
        vencidos = Contrato.objects.filter(dataFinal__lt=timezone.now().date())
        zerados = Contrato.objects.filter(valor__lte=0)
        context = {
            'contratos': contratos,
            'licitacoes': licitacoes,
            'notas_fiscais': notas_fiscais,
            'vencidos': vencidos,
            'zerados': zerados,
            'arps': arp,
        }

        return render(request, 'index.html', context)


# View que Cria os fornecedores
class BiddingFornecedor(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Fornecedor
    form_class = formFornecedor
    template_name = 'fornecedor/fornecedor_new.html'
    success_url = reverse_lazy('biddingContracts:cadContrato')
    permission_required = ["biddingContracts.add_fornecedor"]


def fornecedor_new(request):
    if request.method=='POST':
        form = formFornecedor(request.POST)
        if form.is_valid():
            fornecedor=form.save() 
            print(f"id do fornecedor = {fornecedor.id}")
            #redirecionar de volta para a tela de cadastro fornecendo o ID do fornecedor
            # aqui terá 2 fluxos: 1 redirecionar para a página de contrato e outro para ARP 
            messages.success(request, "Fornecedor cadastrado com sucesso!")
            return redirect('biddingContracts:cadContrato', fornecedor_id = fornecedor.id)
        else:
            print('ocorreu um erro no fomulario', form.errors)
            return render(request, 'fornecedor/fornecedor_new.html', {'form': form})
    else:
        form = formFornecedor()
        return render(request, 'fornecedor/fornecedor_new.html', {'form': form})


# View que lista os fornecedores
@login_required
@permission_required("biddingContracts.view_fornecedor")
def listFornecedores(request):
    fornecedores = Fornecedor.objects.all()
    context = {"fornecedores": fornecedores}
    return render(request, "fornecedor/fornecedores.html", context)


# View que edita os fornecedores
class FornecedorUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model=Fornecedor
    template_name = "fornecedor/fornecedor_update.html"
    form_class = formFornecedor
    context_object_name = "fornecedor"
    permission_required = ["biddingContracts.change_fornecedor"]


    def form_valid(self, form):
        messages.success(self.request, 'fornecedor editado com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar fornecedor. Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("biddingContracts:fornecedores")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
# View que mostra fornecedor em um modal
def modal_fornecedor(request):
    "mostra fornecedor em um modal"
    fornecedores = Fornecedor.objects.all()
    context = {"fornecedores": fornecedores}
    return render(request, "fornecedor/modal_fornecedores.html", context)


# @login_required
# # View que lista as Licitações
# def listLicitacoes(request):
#     """mostra todas as licitacoes"""
#     licitacoes = Licitacao.objects.all()
#     context = {"licitacoes": licitacoes}
#     return render(request, "licitacoes/list_licitacoes.html", context)


@login_required
# View que mostra a licitação em um modal
def modal_licitacao(request):
    "mostra licitacao em um modal"
    licitacoes = Licitacao.objects.all()
    context = {"licitacoes": licitacoes}
    return render(request, "licitacao/modal_bidding.html", context)


# View que faz o cadastro das licitações
class BiddingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Faz o cadastro das licitações
    """
    model = Licitacao
    form_class = formLicitacao
    template_name = 'licitacoes/licitacoes.html'
    message_success = 'Licitação criada com sucesso!'
    permission_required = ["biddingContracts.add_licitacao"]
    

    def get_success_url(self) -> str:
        messages.success(self.request, self.message_success)
        return reverse_lazy('biddingContracts:cadContrato', kwargs={'fornecedor_id':0})


# View que faz a listagem das licitações com a pesquisa 
class ListBiddingView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Faz a listagem das licitações
    """
    model = Licitacao
    template_name = "licitacoes/list_licitacoes.html"
    context_object_name = "licitacoes"
    permission_required = ["biddingContracts.view_licitacao"]

    # Adicionando filtros ao object_list através do get_queryset
    def get_queryset(self):
        txt_licitacao = self.request.GET.get("licitacao")
        txt_assunto = self.request.GET.get("assunto")
        txt_datas = self.request.GET.get("datas")
        txt_categorias = self.request.GET.get("categorias")
        

        if txt_licitacao:
            queryset = Licitacao.objects.filter(numProcess__icontains=txt_licitacao)
            return queryset
        
        elif txt_categorias:
            queryset = Licitacao.objects.filter(categoria__icontains=txt_categorias)
            return queryset
        
        elif txt_datas:
            try:
                data_formatada = datetime.strptime(txt_datas, '%d/%m/%Y').date()
                queryset = Licitacao.objects.filter(date=data_formatada)
                return queryset
            except ValueError:
                messages.error(self.request, 'Data inválida! Por favor, insira uma data no formato dd/mm/yyyy.')
                return redirect('biddingContracts:licitacoes')
        
        elif txt_assunto:
            queryset = Licitacao.objects.filter(assunto__icontains=txt_assunto)
            return queryset
            
        txt_buscar = self.request.GET.get("buscar")
        queryset = Licitacao.objects.all()
        if txt_buscar:
            queryset = queryset.filter(
                Q(categoria__icontains=txt_buscar) |
                Q(assunto__icontains=txt_buscar) |
                Q(numProcess__icontains=txt_buscar)
            )
        else:
            queryset = Licitacao.objects.all()
        return queryset


@login_required
@permission_required("biddingContracts.add_ataregistropreco")
# Função que cria as ARPs
def createArp(request):
    if request.method == "POST":
        form = formARP(request.POST)
        print("enviando método POST")
        if form.is_valid():
            arp = form.save(commit=False)
            dataInicial = arp.dataInicial
            print("formulario valido", dataInicial)
            if dataInicial:
                dataFinal = dataInicial + relativedelta(days=365)
                arp.dataFinal = dataFinal
                print("dataInicial Validada", arp.dataFinal)
            arp.save()
            return HttpResponseRedirect(reverse('biddingContracts:atas'))
    else:
        form = formARP()
    context = {'form': form}
    return render(request, "ARPs/ataRegistroPreco_new.html", context)


# View que lista as ARPs
class listARPs(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model=AtaRegistroPreco
    template_name='ARPs/atas.html'
    success_url= reverse_lazy('biddingContracts:atas')
    context_object_name = "atas"
    permission_required = ["biddingContracts.view_ataregistropreco"]


# View que edita ARPs
class ARPsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model=AtaRegistroPreco
    template_name = "ARPs/ata_update.html"
    form_class = formARP
    context_object_name = "ata"
    permission_required = ["biddingContracts.change_ataregistropreco"]


    def form_valid(self, form):
        messages.success(self.request, 'ARP editada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar ARP. Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("biddingContracts:atas")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# View que deleta as ARPs
class ARPsDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = AtaRegistroPreco
    template_name = "ARPs/ata_delete.html"
    context_object_name = "ata"
    permission_required = ["biddingContracts.delete_ataregistropreco"]
    
    
    
    def get(self, request, *args, **kwargs):
        # Exibir a página de confirmação
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Chama o método delete para excluir o objeto
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Obtém o objeto a ser excluído
        self.object = self.get_object()
        
        # Chama o método delete no objeto
        self.object.delete(usuario=self.request.user)
        
        # Exibe uma mensagem de sucesso e redireciona
        messages.success(self.request, 'Arp excluída com sucesso!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("biddingContracts:atas")


class RelatorioARPs(ListView):
    model = AtaRegistroPreco
    template_name = 'contratos/contratos_relatorio.html'
   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ata_id = self.kwargs.get('pk')  #captura a ata pelo id na url
        notasfiscais = NotaFiscal.objects.filter(ataregistropreco_fk_id = ata_id)
        ata = AtaRegistroPreco.objects.get(id=ata_id) # captura o objeto inteiro

        hoje = datetime.today()
        hoje = hoje.date()
        dataInicial = ata.dataInicial
        dataFinal = ata.dataFinal
        # calculo de quanto tempo falta para o fim da ARP
        prazoRestante = relativedelta(dataFinal,hoje)
        print(hoje)
        #mensagem que será levada para o template
        mensagem=verifica_prazo_validade_arp(prazoRestante, dataFinal, hoje)
        #saldo restante da ARP
        saldoAtual = calcula_saldo_restante(notasfiscais, ata.valor)

        context["vigencia"] = mensagem
        context["hoje"]=hoje
        context["dataFinal"] = dataFinal
        context["prazoRestante"] = prazoRestante
        context["notasfiscais"] = notasfiscais
        context['saldoAtual']=saldoAtual
        context["chave"] = False
        return context

def calcula_saldo_restante(notasfiscais, valorARP):
    soma=0
    for nota in notasfiscais:
        soma+=nota.valor  
    return valorARP - soma
    
    
 # View que atualiza as licitações
class BiddingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Licitacao
    template_name = "licitacoes/edit_licitacoes.html"
    form_class = formLicitacao
    context_object_name = "licitacao"
    permission_required = ["biddingContracts.change_licitacao"]

    def form_valid(self, form):
        messages.success(self.request, 'Licitação editada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar licitação. Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("biddingContracts:list_bidding")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

# #view para salvar as licitações como pdf
# def export_pdf(request): 
#     biddings = Licitacao.objects.all() # lista todas as licitações 
#     html_index = render_to_string('pdf/export-pdf.html', {'licitacoes': biddings})  
#     weasyprint_html = weasyprint.HTML(string=html_index, base_url='http://127.0.0.1:8000/media')
#     pdf = weasyprint_html.write_pdf(stylesheets=[weasyprint.CSS(string='body { font-family: serif} img {margin: 10px; width: 50px;}')]) 
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename=Products'+str(date.today())+'.pdf'
#     response['Content-Transfer-Encoding'] = 'binary'
#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(pdf)
#         output.flush() 
#         output.seek(0)
#         response.write(output.read()) 
#     return response

# # View que cria as notas fiscais
class NotaFiscal_new(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model= NotaFiscal
    form_class = NotaFiscalForm
    template_name = "notafiscal/notaFiscal_new.html"
    success_url = reverse_lazy("biddingContracts:notasfiscais")
    permission_required = ["biddingContracts.add_notafiscal"]

    def get_context_data(self, **kwargs):
        # Captura o valor de is_contract da URL
        context = super().get_context_data(**kwargs)
        is_contract = self.kwargs['is_contract']
        print(type(is_contract))
        context['is_contract'] = is_contract
        return context
    
    def valid_NF_valor(self, valor_nf, valor_contrato, valorTotalNotasFiscais):
        resultado = valorTotalNotasFiscais + valor_nf
        # valida se o resultado da soma ultrapassa o valor total do contrato.
        if resultado > valor_contrato:
            msg_valor="NÃO FOI POSSÍVEL CADASTRAR A NOTA FISCAL, VALOR DA NOTA MAIOR DO QUE O SALDO RESTANTE DO CONTRATO"
            messages.add_message(self.request, messages.ERROR, msg_valor)
            return True
        return False
        
    def valid_NF_vigencia(self, dataHoje, dataFinalContrato):
        if dataFinalContrato<dataHoje:
            msg_vigencia = "NÃO FOI POSSIVEL CADASTRAR NOTAS, CONSULTE O PRAZO RESTANTE DO CONTRATO"
            messages.add_message(self.request, messages.ERROR, msg_vigencia)
            return True
        return False
    
    def search_NF_ByContract(self, id_contrato):
        notafiscal = NotaFiscal.objects.filter(contrato_fk=id_contrato)
        notasfiscais = notafiscal.values_list('valor', flat=True)
        return notasfiscais   

    def searchContractByForn(self, id_fornecedor):
        contratos = Contrato.objects.filter(fornecedor_fk=id_fornecedor.id)
        return contratos
    
    def verificaContratoInserido(self, id_contrato, id_fornecedor):
        contrs = Contrato.objects.filter(fornecedor_fk = id_fornecedor.id)
        print(f"dentro do verificarContratoInserido contratos {id_contrato}, {id_fornecedor}, {contrs}" )
        listaID = contrs.values_list('id', flat=True)
        if id_contrato.id in listaID:
            print("o usuário não modificou o fornecedor após confirmar o modal ")
            return id_contrato
        else:
            print(" o usuario modificou o fornecedor no formulário depois confirmar o modal, atualize o valor do id_contrato (none se tiver vários fornecedores e contrs se tiver apenas 1)")
            if contrs.count()>1:
                return None
            else:
                return contrs.first()
    def form_invalid(self, form):
        print("erro no formulário: ",form.errors)
        messages.error(self.request, 'Erro ao salvar nota fiscal . Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})
        
    def form_valid(self, form):
        dataHoje = datetime.today().date()
        is_contract = self.kwargs['is_contract']
        numNFform = form.cleaned_data['num']
        serieNF = form.cleaned_data['serie']
        valorNFform = form.cleaned_data['valor']
        tipoNF = form.cleaned_data['tipo']
        id_fornecedor = form.cleaned_data['fornecedor_fk']
        id_contrato = form.cleaned_data['contrato_fk']

        context ={
            "numero_nf": numNFform,
            "serie_nf": serieNF,
            "valor_nf": valorNFform,
            "tipo_nf": tipoNF,
            "is_contract": is_contract,
            "form": form
        }
        if is_contract ==1:
            if id_contrato:
                id_contrato = self.verificaContratoInserido(id_contrato, id_fornecedor)
            if id_contrato:                            
                print(f"depois da verificação id_contrato:{id_contrato} tipo: {type(id_contrato)}")
                print(f"depois da verificação id_fornecedor:{id_fornecedor} tipo: {type(id_fornecedor)}")
                
                #retorna uma lista de notas fiscais
                notas=self.search_NF_ByContract(id_contrato) 
                #soma todos os valores retornados
                vlrTotNotas = sum(notas)
                #pega o valor do contrato
                vlr_contrato = id_contrato.valor
                dataHoje = datetime.today().date()
                dataFinalContrato = id_contrato.dataFinal            
                if self.valid_NF_valor(valorNFform, vlr_contrato, vlrTotNotas):
                    return HttpResponseRedirect(reverse('biddingContracts:new_notas', kwargs={'is_contract': is_contract}))
                elif self.valid_NF_vigencia(dataHoje, dataFinalContrato):
                    return HttpResponseRedirect(reverse("biddingContracts:new_notas", kwargs={'is_contract': is_contract}))
                else:
                    print("vai salvar agora", id_fornecedor, id_contrato)
                    nf=form.save(commit=False)
                    nf.contrato_fk = id_contrato
                    nf.save()
                    messages.add_message(self.request, messages.SUCCESS, "SALVO COM SUCESSO")
                    return HttpResponseRedirect(reverse('biddingContracts:notasfiscais', kwargs={'is_contract': is_contract}))
            else:# se o campo id_contrato for None
                contrato = self.searchContractByForn(id_fornecedor)
                print("contrats: ",contrato)
                if contrato.count()>1:
                    context['contratos'] = contrato
                    context['mostramodal'] = True
                    context['fornecedor'] = id_fornecedor

                    return render(self.request, "notafiscal/notaFiscal_new.html", context)
                elif contrato.count()==1:
                    print("para o caso de o fornecedor tiver apenas 1 contrato.")
                    notas=self.search_NF_ByContract(contrato.first().id) 
                    #soma todos os valores retornados
                    vlrTotNotas = sum(notas)
                    #pega o valor do contrato
                    vlr_contrato = contrato.first().valor
                    dataHoje = datetime.today().date()
                    dataFinalContrato = contrato.first().dataFinal            
                    if self.valid_NF_valor(valorNFform, vlr_contrato, vlrTotNotas):
                        return HttpResponseRedirect(reverse('biddingContracts:new_notas', kwargs={'is_contract': is_contract}))
                    elif self.valid_NF_vigencia(dataHoje, dataFinalContrato):
                        return HttpResponseRedirect(reverse("biddingContracts:new_notas", kwargs={'is_contract': is_contract}))
                    else:
                        notafiscal = form.save(commit=False)
                        notafiscal.contrato_fk = contrato.first()
                        notafiscal.save()
                        messages.add_message(self.request, messages.SUCCESS, "SALVO COM SUCESSO")
                        return HttpResponseRedirect(reverse('biddingContracts:notasfiscais', kwargs={'is_contract': is_contract}))
                else:
                    messages.add_message(self.request, messages.WARNING, "NÃO EXISTE CONTRATO PARA ESTE FORNECEDOR")
                    return HttpResponseRedirect(reverse("biddingContracts:new_notas"))       
        else:
            print("notafiscal - ata de registro de preços")
            arp = AtaRegistroPreco.objects.get(numero=form.cleaned_data['ataregistropreco_fk'])
            #pega do banco todas as notas fiscais relacionado a ARP em questão
            notasfiscais = NotaFiscal.objects.filter(ataregistropreco_fk_id = arp.id)
            soma = sum(nota.valor for nota in notasfiscais) + form.cleaned_data.get('valor')
            # valida se o resultado da soma ultrapassa o valor total da ARP
            if soma > arp.valor:
                messages.add_message(self.request, messages.INFO, "NÃO FOI POSSÍVEL CADASTRAR A NOTA FISCAL, VALOR DA NOTA MAIOR DO QUE O SALDO RESTANTE DA ATA DE REGISTRO DE PREÇOS")
                return HttpResponseRedirect(reverse('biddingContracts:new_notas', kwargs={'is_contract': is_contract}))
            #verificação da data de vigência
            if arp.dataFinal < dataHoje:
                messages.add_message(self.request, messages.INFO, "NÃO FOI POSSIVEL CADASTRAR NOTAS, ATA DE REGISTRO DE PREÇOS COM VALIDADE VENCIDA")
                return HttpResponseRedirect(reverse("biddingContracts:new_notas", kwargs={'is_contract': is_contract}))
            # se tiver tudo certo salve os dados.
            form.save()
            messages.add_message(self.request, messages.SUCCESS, "SALVO COM SUCESSO")
            return HttpResponseRedirect(reverse('biddingContracts:notasfiscais', kwargs={'is_contract': is_contract}))
        
# View que lista as Notas Fiscais
class ListNfe(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = NotaFiscal
    template_name = "notafiscal/notasFiscais.html"
    success_url = reverse_lazy("biddingContracts:notasfiscais")
    permission_required = ["biddingContracts.view_notafiscal"]

    def get_context_data(self, **kwargs):
        # Captura o valor de is_contract da URL
        context = super().get_context_data(**kwargs)
        is_contract = self.kwargs['is_contract']
        print(type(is_contract))
        context['is_contract'] = is_contract
        return context


# View que edita as Notas fiscais
class NotasFiscaisUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model=NotaFiscal
    template_name = "notafiscal/notafiscal_update.html"
    form_class = NotaFiscalEditForm
    context_object_name = "notas"
    permission_required = ["biddingContracts.change_notafiscal"]

    def form_valid(self, form):
        messages.success(self.request, 'Nota Fiscal editada com sucesso!')

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar nota fiscal . Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("biddingContracts:notasfiscais", kwargs={'is_contract': 2})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_contract'] = self.kwargs['is_contract']
        is_contract = context['is_contract']
        print(is_contract)
        if (is_contract == 2):
            id_notafiscal = self.kwargs['pk']
           
            notafiscal = NotaFiscal.objects.get(id=id_notafiscal)
            print(" numero da nota fiscal é:", notafiscal.num)
            if notafiscal.ataregistropreco_fk is None:
                context["is_contract"] = 1
            elif notafiscal.contrato_fk is None:
                context["is_contract"] = 0
            
        return context
    
from django.core.exceptions import PermissionDenied
    
# View que deleta as Notas fiscais

class NotesDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = NotaFiscal
    template_name = "notafiscal/nota_delete.html"  # Página de confirmação
    context_object_name = "note"
    permission_required = ["biddingContracts.delete_notafiscal"]

    def get(self, request, *args, **kwargs):
        # Exibir a página de confirmação
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Chama o método delete para excluir o objeto
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Obtém o objeto a ser excluído
        self.object = self.get_object()
        
        # Chama o método delete no objeto
        self.object.delete(usuario=self.request.user)
        
        # Exibe uma mensagem de sucesso e redireciona
        messages.success(self.request, 'Nota Fiscal (ARP) excluída com sucesso!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("biddingContracts:notasfiscais", kwargs={"is_contract": 2})
    
# View que cria as secretarias
class SecretaryNew(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

    """
    Faz o cadastro das Secretarias
    """
    model = Secretaria
    form_class = formSecretaria
    template_name = 'secretaria/secretaria_new.html'
    message_success = 'Secretaria cadastrada com sucesso!'
    permission_required = ["biddingContracts.add_secretaria"]

    def get_success_url(self) -> str:
        messages.success(self.request, self.message_success)
        return reverse_lazy('biddingContracts:list_secretarias')
    


# View que lista as Secretarias
class ListSecretary(LoginRequiredMixin, ListView):
    model = Secretaria
    template_name = "secretaria/list_secretaria.html"
    success_url = reverse_lazy("biddingContracts:list_secretarias")
    context_object_name = "secretarias"
    permission_required = ["biddingContracts.view_secretaria"]


 # View que edita as secretarias 
class SecretaryUpdateView(LoginRequiredMixin, UpdateView):
    model = Secretaria
    template_name = "secretaria/edit_secretarias.html"
    form_class = formSecretaria
    context_object_name = "secretaria"

    def form_valid(self, form):
        messages.success(self.request, 'Secretaria editada com sucesso!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Erro ao editar secretaria. Verifique os campos do formulário.')
        return render(self.request, self.template_name, {"form": form})

    def get_success_url(self):
        return reverse_lazy("biddingContracts:list_secretarias")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    
@login_required
# View que mostra fornecedor em um modal
def modal_secretaria(request):
    "mostra fornecedor em um modal"
    secretarias = Secretaria.objects.all()
    context = {"secretarias": secretarias}
    return render(request, "secretaria/modal_secretaria.html", context)


# View que deleta as Secretarias
class SecretaryDeleteView(LoginRequiredMixin, DeleteView):
    model = Secretaria
    template_name = "secretaria/delete_secretaria.html"
    context_object_name = "sec"
    #permission_required = ["biddingContracts.delete_secretaria"]

    def get(self, request, *args, **kwargs):
        # Exibir a página de confirmação
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # Chama o método delete para excluir o objeto
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Obtém o objeto a ser excluído
        self.object = self.get_object()
        
        # Chama o método delete no objeto
        self.object.delete(usuario=self.request.user)
        
        # Exibe uma mensagem de sucesso e redireciona
        messages.success(self.request, 'Secretaria excluída com sucesso!')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("biddingContracts:list_secretarias")
    


# def registros_excluidos(request):
#     registros = RegistroExcluido.objects.all()
#     return render(request, 'excluidos/registros_excluidos.html', {'registros': registros})


# View para exibir template dos dados excluídos
class ListRegister(ListView):
    model = RegistroExcluido
    template_name = "excluidos/registros_excluidos.html"
    context_object_name = "registros"
    # paginate_by = 10
    # ordering = ['-id']
    #permission_required = ["biddingContracts.list_registroexcluido"]
    
    
    # Adicionando filtros ao object_list através do get_queryset
    def get_queryset(self):
        txt_modelo = self.request.GET.get("modelos")
        txt_usuario = self.request.GET.get("usuarios")
        txt_datas = self.request.GET.get("datas")
        
        queryset = RegistroExcluido.objects.all()
        
        
        if txt_modelo:
            queryset = RegistroExcluido.objects.filter(modelo__icontains=txt_modelo)
            return queryset
        
        elif txt_usuario:
            queryset = RegistroExcluido.objects.filter(usuario__username__icontains=txt_usuario)
            return queryset
        
        elif txt_datas:
            try:
                data_formatada = datetime.strptime(txt_datas, '%d/%m/%Y').date()
                queryset = RegistroExcluido.objects.filter(data_exclusao=data_formatada)
                return queryset
            except ValueError:
                messages.error(self.request, 'Data inválida! Por favor, insira uma data no formato dd/mm/yyyy.')
                return redirect('biddingContracts:excluidos')      
        else:
            queryset = RegistroExcluido.objects.all()
        return queryset
        