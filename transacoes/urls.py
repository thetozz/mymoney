from django.urls import path
from . import views

app_name = 'transacoes'

urlpatterns = [
    # Transações
    path('', views.lista_transacoes, name='lista'),
    path('nova/', views.criar_transacao, name='criar'),
    path('<int:pk>/editar/', views.editar_transacao, name='editar'),
    path('<int:pk>/excluir/', views.excluir_transacao, name='excluir'),

    # Categorias
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/nova/', views.criar_categoria, name='criar_categoria'),

    # Importação OFX
    path('importar-ofx/', views.importar_ofx, name='importar_ofx'),
]
