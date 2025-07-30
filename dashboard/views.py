from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from transacoes.models import Transacao, Categoria, TransacaoRecorrente
import json
import calendar


def calcular_transacoes_previstas(usuario, mes, ano):
    """Calcula transações recorrentes previstas para um mês específico"""
    # Busca todas as transações recorrentes ativas do usuário
    recorrentes = TransacaoRecorrente.objects.filter(
        usuario=usuario,
        ativa=True
    )
    
    transacoes_previstas = []
    
    for recorrente in recorrentes:
        # Verifica se deve gerar para este mês
        data_mes = datetime(ano, mes, 1).date()
        
        # Verifica se está dentro do período de vigência
        if data_mes < recorrente.data_inicio:
            continue
            
        if recorrente.data_fim and data_mes > recorrente.data_fim:
            continue
        
        # Calcula se deve gerar baseado na recorrência
        deve_gerar = False
        
        if recorrente.tipo_recorrencia == 'MENSAL':
            deve_gerar = True
        elif recorrente.tipo_recorrencia == 'BIMESTRAL':
            # A cada 2 meses a partir da data de início
            diff_meses = (ano - recorrente.data_inicio.year) * 12 + (mes - recorrente.data_inicio.month)
            deve_gerar = diff_meses % 2 == 0
        elif recorrente.tipo_recorrencia == 'TRIMESTRAL':
            # A cada 3 meses
            diff_meses = (ano - recorrente.data_inicio.year) * 12 + (mes - recorrente.data_inicio.month)
            deve_gerar = diff_meses % 3 == 0
        elif recorrente.tipo_recorrencia == 'SEMESTRAL':
            # A cada 6 meses
            diff_meses = (ano - recorrente.data_inicio.year) * 12 + (mes - recorrente.data_inicio.month)
            deve_gerar = diff_meses % 6 == 0
        elif recorrente.tipo_recorrencia == 'ANUAL':
            # Todo ano no mesmo mês da data de início
            deve_gerar = mes == recorrente.data_inicio.month
        
        if deve_gerar:
            # Verifica se já existe transação real para este período
            identificador = f"recorrente_{recorrente.id}_{mes}_{ano}"
            transacao_existe = Transacao.objects.filter(
                usuario=usuario,
                identificador_ofx=identificador
            ).exists()
            
            if not transacao_existe:
                # Calcula a data prevista
                ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
                dia_ajustado = min(recorrente.dia_vencimento, ultimo_dia_mes)
                data_prevista = datetime(ano, mes, dia_ajustado).date()
                
                transacoes_previstas.append({
                    'descricao': f"{recorrente.descricao} (Prevista)",
                    'valor': recorrente.valor,
                    'tipo': recorrente.tipo,
                    'data': data_prevista,
                    'categoria': recorrente.categoria,
                    'conta_bancaria': recorrente.conta_bancaria,
                    'recorrente_id': recorrente.id,
                    'eh_prevista': True
                })
    
    return transacoes_previstas


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

    # Cálculos financeiros das transações reais
    receitas_total = transacoes_base.filter(tipo='RECEITA').aggregate(
        total=Sum('valor'))['total'] or 0
    despesas_total = transacoes_base.filter(tipo='DESPESA').aggregate(
        total=Sum('valor'))['total'] or 0
    saldo_mes = receitas_total - despesas_total

    # Calcula transações previstas (recorrentes não consolidadas)
    transacoes_previstas = calcular_transacoes_previstas(
        request.user, mes, ano
    )
    
    # Separa receitas e despesas previstas
    receitas_previstas = [t for t in transacoes_previstas if t['tipo'] == 'RECEITA']
    despesas_previstas = [t for t in transacoes_previstas if t['tipo'] == 'DESPESA']
    
    # Totais das transações previstas
    receitas_previstas_total = sum(float(t['valor']) for t in receitas_previstas)
    despesas_previstas_total = sum(float(t['valor']) for t in despesas_previstas)
    
    # Totais projetados (reais + previstas)
    receitas_projetadas = receitas_total + receitas_previstas_total
    despesas_projetadas = despesas_total + despesas_previstas_total
    saldo_projetado = receitas_projetadas - despesas_projetadas

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
        # Dados das transações previstas
        'receitas_previstas': receitas_previstas,
        'despesas_previstas': despesas_previstas,
        'receitas_previstas_total': receitas_previstas_total,
        'despesas_previstas_total': despesas_previstas_total,
        'receitas_projetadas': receitas_projetadas,
        'despesas_projetadas': despesas_projetadas,
        'saldo_projetado': saldo_projetado,
        'tem_previstas': len(transacoes_previstas) > 0,
        'meses': [
            (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'),
            (4, 'Abril'), (5, 'Maio'), (6, 'Junho'),
            (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
            (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
        ],
        'anos': range(2020, timezone.now().year + 2)
    }

    return render(request, 'dashboard/home.html', context)


@login_required
def consolidar_transacao_prevista(request, recorrente_id, mes, ano):
    """Consolida uma transação prevista criando a transação real"""
    if request.method == 'POST':
        from django.shortcuts import get_object_or_404
        from django.contrib import messages
        from django.shortcuts import redirect
        
        # Busca a transação recorrente
        recorrente = get_object_or_404(
            TransacaoRecorrente, 
            id=recorrente_id, 
            usuario=request.user
        )
        
        # Gera a transação para o mês especificado
        transacao = recorrente.gerar_transacao_mes(mes, ano)
        
        if transacao:
            transacao.save()
            messages.success(
                request, 
                f'Transação "{recorrente.descricao}" consolidada com sucesso!'
            )
        else:
            messages.error(
                request, 
                'Erro ao consolidar transação. Ela pode já ter sido criada.'
            )
    
    return redirect('dashboard:home')
