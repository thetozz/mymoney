from django.contrib import admin
from .models import Categoria, ContaBancaria, Transacao, ImportacaoOFX


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'usuario', 'ativa']
    list_filter = ['tipo', 'ativa', 'usuario']
    search_fields = ['nome']
    list_per_page = 50

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


from django.contrib import admin
from .models import Categoria, ContaBancaria, Transacao, TransacaoRecorrente, ImportacaoOFX


from django.contrib import admin
from .models import (Categoria, ContaBancaria, Transacao, 
                     TransacaoRecorrente, ImportacaoOFX)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'usuario', 'ativa']
    list_filter = ['tipo', 'ativa', 'usuario']
    search_fields = ['nome']
    list_per_page = 50
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'banco', 'agencia', 'conta', 
                    'saldo_inicial', 'usuario', 'ativa']
    list_filter = ['banco', 'ativa', 'usuario']
    search_fields = ['nome', 'banco']
    list_per_page = 50
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'data', 
                    'categoria', 'conta_bancaria', 'usuario']
    list_filter = ['tipo', 'data', 'categoria', 'importada_ofx', 'usuario']
    search_fields = ['descricao', 'identificador_ofx']
    date_hierarchy = 'data'
    list_per_page = 100
    readonly_fields = ['criado_em', 'atualizado_em']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(TransacaoRecorrente)
class TransacaoRecorrenteAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'tipo_recorrencia', 
                    'dia_vencimento', 'ativa', 'usuario']
    list_filter = ['tipo', 'tipo_recorrencia', 'ativa', 'usuario']
    search_fields = ['descricao']
    list_per_page = 50
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'valor', 'tipo', 'categoria', 
                      'conta_bancaria')
        }),
        ('Configurações de Recorrência', {
            'fields': ('tipo_recorrencia', 'dia_vencimento', 'data_inicio', 
                      'data_fim', 'ativa')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImportacaoOFX)
class ImportacaoOFXAdmin(admin.ModelAdmin):
    list_display = ['arquivo_nome', 'data_importacao', 'usuario', 
                    'total_transacoes', 'transacoes_importadas', 
                    'transacoes_duplicadas', 'sucesso']
    list_filter = ['sucesso', 'data_importacao', 'usuario']
    search_fields = ['arquivo_nome']
    date_hierarchy = 'data_importacao'
    readonly_fields = ['data_importacao']
    list_per_page = 50


@admin.register(ContaBancaria)
class ContaBancariaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'banco', 'agencia', 'conta', 'saldo_inicial', 'usuario', 'ativa']
    list_filter = ['banco', 'ativa', 'usuario']
    search_fields = ['nome', 'banco']
    list_per_page = 50
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'data', 'categoria', 'conta_bancaria', 'usuario']
    list_filter = ['tipo', 'data', 'categoria', 'importada_ofx', 'usuario']
    search_fields = ['descricao', 'identificador_ofx']
    date_hierarchy = 'data'
    list_per_page = 100
    readonly_fields = ['criado_em', 'atualizado_em']
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(TransacaoRecorrente)
class TransacaoRecorrenteAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo', 'tipo_recorrencia', 'dia_vencimento', 'ativa', 'usuario']
    list_filter = ['tipo', 'tipo_recorrencia', 'ativa', 'usuario']
    search_fields = ['descricao']
    list_per_page = 50
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('descricao', 'valor', 'tipo', 'categoria', 'conta_bancaria')
        }),
        ('Configurações de Recorrência', {
            'fields': ('tipo_recorrencia', 'dia_vencimento', 'data_inicio', 'data_fim', 'ativa')
        }),
        ('Auditoria', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImportacaoOFX)
class ImportacaoOFXAdmin(admin.ModelAdmin):
    list_display = ['arquivo_nome', 'data_importacao', 'usuario', 'total_transacoes',
                    'transacoes_importadas', 'transacoes_duplicadas', 'sucesso']
    list_filter = ['sucesso', 'data_importacao', 'usuario']
    search_fields = ['arquivo_nome']
    date_hierarchy = 'data_importacao'
    readonly_fields = ['data_importacao']
    list_per_page = 50


@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    list_display = ['descricao', 'valor', 'tipo',
                    'data', 'categoria', 'conta_bancaria', 'usuario']
    list_filter = ['tipo', 'data', 'categoria', 'importada_ofx', 'usuario']
    search_fields = ['descricao', 'identificador_ofx']
    date_hierarchy = 'data'
    list_per_page = 100
    readonly_fields = ['criado_em', 'atualizado_em']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)


@admin.register(ImportacaoOFX)
class ImportacaoOFXAdmin(admin.ModelAdmin):
    list_display = ['arquivo_nome', 'data_importacao', 'usuario', 'total_transacoes',
                    'transacoes_importadas', 'transacoes_duplicadas', 'sucesso']
    list_filter = ['sucesso', 'data_importacao', 'usuario']
    search_fields = ['arquivo_nome']
    date_hierarchy = 'data_importacao'
    readonly_fields = ['data_importacao']
    list_per_page = 50
