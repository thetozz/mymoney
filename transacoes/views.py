from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import (
    Transacao, Categoria, ContaBancaria, ImportacaoOFX, TransacaoRecorrente
)
from .forms import (
    TransacaoForm, CategoriaForm, ContaBancariaForm, TransacaoRecorrenteForm
)
from .utils import (
    processar_arquivo_ofx, preview_arquivo_ofx, salvar_transacoes_ofx
)
import json


@login_required
def lista_transacoes(request):
    """Lista todas as transações do usuário com filtros"""
    transacoes = Transacao.objects.filter(usuario=request.user)

    # Filtros
    tipo = request.GET.get('tipo')
    categoria_id = request.GET.get('categoria')
    busca = request.GET.get('busca')

    if tipo:
        transacoes = transacoes.filter(tipo=tipo)
    if categoria_id:
        transacoes = transacoes.filter(categoria_id=categoria_id)
    if busca:
        transacoes = transacoes.filter(
            Q(descricao__icontains=busca) | Q(categoria__nome__icontains=busca)
        )

    # Paginação
    paginator = Paginator(transacoes, 20)
    page = request.GET.get('page')
    transacoes = paginator.get_page(page)

    categorias = Categoria.objects.filter(usuario=request.user, ativa=True)

    context = {
        'transacoes': transacoes,
        'categorias': categorias,
        'filtro_tipo': tipo,
        'filtro_categoria': categoria_id,
        'busca': busca,
    }

    return render(request, 'transacoes/lista.html', context)


@login_required
def criar_transacao(request):
    """Cria uma nova transação"""
    if request.method == 'POST':
        form = TransacaoForm(request.POST, user=request.user)
        if form.is_valid():
            transacao = form.save(commit=False)
            transacao.usuario = request.user
            transacao.save()
            messages.success(request, 'Transação criada com sucesso!')
            return redirect('transacoes:lista')
    else:
        form = TransacaoForm(user=request.user)

    return render(request, 'transacoes/form.html', {
        'form': form,
        'titulo': 'Nova Transação'
    })


@login_required
def editar_transacao(request, pk):
    """Edita uma transação existente"""
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = TransacaoForm(
            request.POST, instance=transacao, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transação atualizada com sucesso!')
            return redirect('transacoes:lista')
    else:
        form = TransacaoForm(instance=transacao, user=request.user)

    return render(request, 'transacoes/form.html', {
        'form': form,
        'titulo': 'Editar Transação',
        'transacao': transacao
    })


@login_required
def excluir_transacao(request, pk):
    """Exclui uma transação"""
    transacao = get_object_or_404(Transacao, pk=pk, usuario=request.user)

    if request.method == 'POST':
        transacao.delete()
        messages.success(request, 'Transação excluída com sucesso!')
        return redirect('transacoes:lista')

    return render(request, 'transacoes/confirmar_exclusao.html', {
        'transacao': transacao
    })


@login_required
def lista_categorias(request):
    """Lista todas as categorias do usuário"""
    categorias = Categoria.objects.filter(usuario=request.user)

    return render(request, 'transacoes/categorias.html', {
        'categorias': categorias
    })


@login_required
def criar_categoria(request):
    """Cria uma nova categoria"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('transacoes:categorias')
    else:
        form = CategoriaForm()

    return render(request, 'transacoes/categoria_form.html', {
        'form': form,
        'titulo': 'Nova Categoria'
    })


@login_required
def importar_ofx(request):
    """Importa arquivo OFX - Etapa 1: Upload e preview"""
    if request.method == 'POST' and request.FILES.get('arquivo_ofx'):
        arquivo = request.FILES['arquivo_ofx']
        conta_id = request.POST.get('conta_bancaria')

        try:
            conta = None
            if conta_id:
                conta = get_object_or_404(
                    ContaBancaria, pk=conta_id, usuario=request.user)

            # Processa o arquivo sem salvar as transações
            resultado = preview_arquivo_ofx(arquivo, request.user, conta)

            if resultado['sucesso']:
                # Armazena os dados na sessão para confirmação
                request.session['preview_transacoes'] = resultado['transacoes']
                request.session['preview_conta_id'] = conta_id
                request.session['preview_arquivo_nome'] = arquivo.name

                return redirect('transacoes:confirmar_importacao_ofx')
            else:
                messages.error(
                    request, f'Erro no processamento: {resultado["erro"]}')

        except Exception as e:
            messages.error(request, f'Erro ao processar arquivo: {str(e)}')

        return redirect('transacoes:importar_ofx')

    contas = ContaBancaria.objects.filter(usuario=request.user, ativa=True)
    importacoes = ImportacaoOFX.objects.filter(usuario=request.user)[:10]

    return render(request, 'transacoes/importar_ofx.html', {
        'contas': contas,
        'importacoes': importacoes
    })


@login_required
def confirmar_importacao_ofx(request):
    """Confirma importação OFX - Etapa 2: Preview e confirmação"""
    transacoes_preview = request.session.get('preview_transacoes')
    conta_id = request.session.get('preview_conta_id')
    arquivo_nome = request.session.get('preview_arquivo_nome')

    if not transacoes_preview:
        messages.error(
            request,
            'Dados de importação não encontrados. Tente novamente.'
        )
        return redirect('transacoes:importar_ofx')

    if request.method == 'POST':
        if request.POST.get('confirmar') == 'sim':
            # Salva as transações confirmadas
            resultado = salvar_transacoes_ofx(
                transacoes_preview,
                request.user,
                conta_id,
                arquivo_nome
            )

            if resultado['sucesso']:
                messages.success(
                    request,
                    f'Importação concluída! {resultado["importadas"]} '
                    f'transações importadas, {resultado["duplicadas"]} '
                    f'duplicatas ignoradas.'
                )
            else:
                messages.error(
                    request, f'Erro na importação: {resultado["erro"]}')

        # Limpa dados da sessão
        request.session.pop('preview_transacoes', None)
        request.session.pop('preview_conta_id', None)
        request.session.pop('preview_arquivo_nome', None)

        return redirect('transacoes:importar_ofx')

    # Busca categorias para possível edição
    categorias = Categoria.objects.filter(usuario=request.user, ativa=True)
    conta = None
    if conta_id:
        conta = get_object_or_404(
            ContaBancaria, pk=conta_id, usuario=request.user
        )

    return render(request, 'transacoes/confirmar_importacao_ofx.html', {
        'transacoes': transacoes_preview,
        'categorias': categorias,
        'conta': conta,
        'arquivo_nome': arquivo_nome,
        'total_transacoes': len(transacoes_preview),
        'chatgpt_enabled': getattr(settings, 'CHATGPT_ENABLED', False)
    })


@login_required
def lista_transacoes_recorrentes(request):
    """Lista todas as transações recorrentes do usuário"""
    recorrentes = TransacaoRecorrente.objects.filter(
        usuario=request.user
    ).order_by('-data_fim')

    # Filtros
    tipo = request.GET.get('tipo')
    ativa = request.GET.get('ativa')
    busca = request.GET.get('busca')

    if tipo:
        recorrentes = recorrentes.filter(tipo=tipo)
    if ativa is not None:
        recorrentes = recorrentes.filter(ativa=ativa == 'true')
    if busca:
        recorrentes = recorrentes.filter(
            Q(descricao__icontains=busca) |
            Q(categoria__nome__icontains=busca)
        )

    # Paginação
    paginator = Paginator(recorrentes, 20)
    page = request.GET.get('page')
    recorrentes = paginator.get_page(page)

    context = {
        'recorrentes': recorrentes,
        'filtro_tipo': tipo,
        'filtro_ativa': ativa,
        'busca': busca,
    }

    return render(request, 'transacoes/recorrentes_lista.html', context)


@login_required
def criar_transacao_recorrente(request):
    """Cria uma nova transação recorrente"""
    if request.method == 'POST':
        form = TransacaoRecorrenteForm(request.POST, user=request.user)
        if form.is_valid():
            recorrente = form.save(commit=False)
            recorrente.usuario = request.user
            recorrente.save()
            messages.success(
                request, 'Transação recorrente criada com sucesso!'
            )
            return redirect('transacoes:recorrentes')
    else:
        form = TransacaoRecorrenteForm(user=request.user)

    return render(request, 'transacoes/recorrente_form.html', {
        'form': form,
        'titulo': 'Nova Transação Recorrente'
    })


@login_required
def editar_transacao_recorrente(request, pk):
    """Edita uma transação recorrente existente"""
    recorrente = get_object_or_404(
        TransacaoRecorrente, pk=pk, usuario=request.user
    )

    if request.method == 'POST':
        form = TransacaoRecorrenteForm(
            request.POST, instance=recorrente, user=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Transação recorrente atualizada com sucesso!'
            )
            return redirect('transacoes:recorrentes')
    else:
        form = TransacaoRecorrenteForm(instance=recorrente, user=request.user)

    return render(request, 'transacoes/recorrente_form.html', {
        'form': form,
        'titulo': 'Editar Transação Recorrente',
        'recorrente': recorrente
    })


@login_required
def excluir_transacao_recorrente(request, pk):
    """Exclui uma transação recorrente"""
    recorrente = get_object_or_404(
        TransacaoRecorrente, pk=pk, usuario=request.user
    )

    if request.method == 'POST':
        recorrente.delete()
        messages.success(
            request, 'Transação recorrente excluída com sucesso!'
        )
        return redirect('transacoes:recorrentes')

    return render(request, 'transacoes/recorrente_confirmar_exclusao.html', {
        'recorrente': recorrente
    })


@login_required
def gerar_transacoes_mes(request):
    """Gera todas as transações recorrentes para o mês atual"""
    if request.method == 'POST':
        from django.utils import timezone

        now = timezone.now()
        mes_atual = now.month
        ano_atual = now.year

        recorrentes = TransacaoRecorrente.objects.filter(
            usuario=request.user, ativa=True
        )

        total_geradas = 0
        for recorrente in recorrentes:
            transacao = recorrente.gerar_transacao_mes(mes_atual, ano_atual)
            if transacao:
                transacao.save()
                total_geradas += 1

        if total_geradas > 0:
            messages.success(
                request,
                f'{total_geradas} transações geradas para este mês!'
            )
        else:
            messages.info(
                request,
                'Nenhuma transação nova foi gerada. '
                'Todas as transações do mês já existem.'
            )

        return redirect('transacoes:recorrentes')

    return redirect('transacoes:recorrentes')
