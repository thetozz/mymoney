from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('consolidar/<int:recorrente_id>/<int:mes>/<int:ano>/', 
         views.consolidar_transacao_prevista, name='consolidar_prevista'),
]
