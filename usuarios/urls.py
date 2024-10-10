from django.urls import path

from usuarios import views, views2
from django.contrib.auth.views import LoginView

app_name = "usuarios"

urlpatterns = [
    path('cadastro/', views2.cadastro, name="register"),
    path('login/', views2.login, name='login'),
    path('logout/', views2.logout, name='logout'),
    path('password_reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/add-permission/<int:pk>', views.add_permission, name='add_permission'),
    
    # Cadastro de usuśrios secretaria
    path('cadastro/membros-secretaria/', views2.cadastro_secretaria, name='cad_user'),
    path('listar/membros-secretaria/', views2.ListMemberView.as_view(), name='list_member'),
    #path('cadastro/membros-secretaria/<int:pk>/update/', views2.update_user_secret.as_view(), name='cad_update'),

    # Detalhe do usuário
    path('dashboard/usuario/<int:pk>/', views2.DetailMemberView.as_view(), name="detail_member"),
]

