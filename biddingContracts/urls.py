from . import views, views_dash
from django.urls import path

app_name = 'biddingContracts'

urlpatterns = [
    path('', views.index, name='index'),

    # Contratos
    path('contrato/<int:fornecedor_id>', views.cadContrato, name="cadContrato"), # Cadastra Contratos
    path("contratos/", views.ListContractsView.as_view(), name="contratos"), # Lista Contratos
    path('contratos/relatorio/<int:id_contrato>', views.contratosRelatorio, name='relatorio'), # Relatório dos contratos
    path('contratos/<int:pk>/editar/', views.ContractsUpdateView.as_view(), name='update_contracts'), # Atualiza Contratos
    path('delete/contract/<int:pk>/', views.ContractDeleteView.as_view(), name='delete_contracts'), # Deleta contratos

    # Fornecedores
    path('fornecedores/', views.listFornecedores, name="fornecedores"), # Lista Fornecedores
    path('criar-fornecedor/', views.fornecedor_new, name='fornecedor_new'), # Cadastra Fornecedores
    path('modal-fornecedor/', views.modal_fornecedor, name="modal-fornecedor"), # Modal Fornecedor
    path('updt-fornecedor/<int:pk>/', views.FornecedorUpdate.as_view(), name='updateforn'), # Atualiza Fornecedor

    # Licitações
    path('criar-licitacoes/', views.BiddingCreateView.as_view(), name='create-bidding'), # Criar Licitações
    path('licitacoes/', views.ListBiddingView.as_view(), name="list_bidding"), # Listar Licitações
    path('licitacoes/<int:pk>/editar/', views.BiddingUpdateView.as_view(), name='update_bidding'), # Atualiza Licitações
    path('modal-licitacao/', views.modal_licitacao, name='modal-licitacao'), # Modal Licitação
    #path('export-pdf/', views.export_pdf, name='export-pdf'),
    
    # ARPs
    path('criar-ARP/', views.createArp, name='create-ARP'), # Criar ARPs
    path('atas/', views.listARPs.as_view(), name="atas"), # Listar ARPs
    path('relatorio-atas/<int:pk>', views.RelatorioARPs.as_view(), name='relatorioARP'), # Relatório ARPs
    path('atas-edit/<int:pk>/', views.ARPsUpdate.as_view(), name="updateARP"), # Editar ARPS
    path('atas-delete/<int:pk>/', views.ARPsDeleteView.as_view(), name="deleteARP"), # Deletar ARPS

    # Notas Fiscais
    path('create/nota/fiscal/<int:is_contract>/', views.NotaFiscal_new.as_view(), name='new_notas'), # Criar Notas Fiscais
    path('notasfiscais/<int:is_contract>/', views.ListNfe.as_view(), name='notasfiscais'), # Listar Notas Fiscais
    path('editarnfe/<int:pk>/<int:is_contract>/', views.NotasFiscaisUpdate.as_view(), name='updatenfe'), # Editar Notas Fiscais
    path('deletenfe/<int:pk>/', views.NotesDeleteView.as_view(), name='deletenfe'), # Deletar Notas Fiscais

    # Secretarias
    path('create/new-secretary/', views.SecretaryNew.as_view(), name='new_secretaria'),# Criar Secretarias
    path('list-secretarys/', views.ListSecretary.as_view(), name='list_secretarias'), # Listar Secretarias
    path('modal-secretaria/', views.modal_secretaria, name="modal_secretaria"), #Modal Secretaria
    path('editar-secretaria/<int:pk>/', views.SecretaryUpdateView.as_view(), name='update_secretaria'), # Editar Secretarias
    path('delete-secretary/<int:pk>/', views.SecretaryDeleteView.as_view(), name='del_secretaria'), # Deletar secretarias
    
    # Dashboard
    path('teste/', views_dash.retorna_total_valores, name="teste"),
    path('teste2/', views_dash.contrato_valor_por_mes, name="teste2"),

    # Excluídos
    path('excluidos/', views.ListRegister.as_view(), name="excluidos")

]
