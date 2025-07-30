from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from transacoes.models import Transacao, Categoria
import json


@login_required
def home_view(request):
    """Dashboard principal com resumo financeiro"""
    # Filtros de período
    mes_atual = timezone.now().month
    ano_atual = timezone.now().year

    # Parâmetros de filtro da URL
    mes = int(request.GET.get('mes', mes_atual))
    ano = int(request.GET.get('ano', ano_atual))

    # Se não houver transações no mês atual, mostra o último mês com transações
    transacoes_teste = Transacao.objects.filter(
        usuario=request.user,
        data__month=mes,
        data__year=ano
    ).exists()

    if not transacoes_teste and not request.GET.get('mes'):
        # Busca o último mês com transações
        ultima_transacao = Transacao.objects.filter(
            usuario=request.user
        ).order_by('-data').first()

        if ultima_transacao:
            mes = ultima_transacao.data.month
            ano = ultima_transacao.data.year

    # Query base filtrada por usuário e período
    transacoes_base = Transacao.objects.filter(
        usuario=request.user,
        data__month=mes,
        data__year=ano
    )

    # Cálculos financeiros
    receitas_total = transacoes_base.filter(tipo='RECEITA').aggregate(
        total=Sum('valor'))['total'] or 0
    despesas_total = transacoes_base.filter(tipo='DESPESA').aggregate(
        total=Sum('valor'))['total'] or 0
    saldo_mes = receitas_total - despesas_total

    # Receitas e despesas por categoria
    receitas_categoria = transacoes_base.filter(tipo='RECEITA').values(
        'categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')).order_by('-total')

    despesas_categoria = transacoes_base.filter(tipo='DESPESA').values(
        'categoria__nome', 'categoria__cor').annotate(
        total=Sum('valor')).order_by('-total')

    # Transações recentes
    transacoes_recentes = transacoes_base.order_by('-data', '-criado_em')[:10]

    # Dados para gráficos (JSON)
    receitas_chart_data = {
        'labels': [item['categoria__nome'] for item in receitas_categoria],
        'data': [float(item['total']) for item in receitas_categoria],
        'colors': [item['categoria__cor'] for item in receitas_categoria]
    }

    despesas_chart_data = {
        'labels': [item['categoria__nome'] for item in despesas_categoria],
        'data': [float(item['total']) for item in despesas_categoria],
        'colors': [item['categoria__cor'] for item in despesas_categoria]
    }

    # Histórico dos últimos 12 meses
    historico_meses = []
    for i in range(12):
        data_mes = timezone.now() - timedelta(days=30*i)
        transacoes_mes = Transacao.objects.filter(
            usuario=request.user,
            data__month=data_mes.month,
            data__year=data_mes.year
        )
        receitas_mes = transacoes_mes.filter(tipo='RECEITA').aggregate(
            total=Sum('valor'))['total'] or 0
        despesas_mes = transacoes_mes.filter(tipo='DESPESA').aggregate(
            total=Sum('valor'))['total'] or 0

        historico_meses.append({
            'mes': data_mes.strftime('%m/%Y'),
            'receitas': float(receitas_mes),
            'despesas': float(despesas_mes),
            'saldo': float(receitas_mes - despesas_mes)
        })

    historico_meses.reverse()

    # Verifica se estamos mostrando dados do mês atual ou de outro período
    mostrando_mes_atual = (mes == mes_atual and ano == ano_atual)

    context = {
        'receitas_total': receitas_total,
        'despesas_total': despesas_total,
        'saldo_mes': saldo_mes,
        'receitas_categoria': receitas_categoria,
        'despesas_categoria': despesas_categoria,
        'transacoes_recentes': transacoes_recentes,
        'receitas_chart_data': json.dumps(receitas_chart_data),
        'despesas_chart_data': json.dumps(despesas_chart_data),
        'historico_meses': json.dumps(historico_meses),
        'mes_atual': mes,
        'ano_atual': ano,
        'mostrando_mes_atual': mostrando_mes_atual,
        'meses': [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
            (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
            (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
            (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ],
        'anos': range(2020, timezone.now().year + 2)
    }

    return render(request, 'dashboard/home.html', context)
