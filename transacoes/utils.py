import ofxparse
from decimal import Decimal
from django.utils import timezone
from .models import Transacao, ImportacaoOFX, Categoria


def processar_arquivo_ofx(arquivo, usuario, conta_bancaria=None):
    """
    Processa um arquivo OFX e importa as transações

    Args:
        arquivo: Arquivo OFX enviado
        usuario: Usuário que está importando
        conta_bancaria: Conta bancária associada (opcional)

    Returns:
        dict: Resultado da importação com estatísticas
    """
    try:
        # Parse do arquivo OFX
        ofx = ofxparse.OfxParser.parse(arquivo)

        # Cria registro de importação
        importacao = ImportacaoOFX.objects.create(
            arquivo_nome=arquivo.name,
            usuario=usuario,
            total_transacoes=0,
            transacoes_importadas=0,
            transacoes_duplicadas=0
        )

        transacoes_importadas = 0
        transacoes_duplicadas = 0
        total_transacoes = 0

        # Processa cada conta no arquivo OFX
        for account in ofx.accounts:
            for transaction in account.statement.transactions:
                total_transacoes += 1

                # Cria identificador único baseado nos dados da transação
                identificador = f"{account.account_id}_{transaction.id}_{transaction.date}_{transaction.amount}"

                # Verifica se já existe uma transação com esse identificador
                if Transacao.objects.filter(
                    usuario=usuario,
                    identificador_ofx=identificador
                ).exists():
                    transacoes_duplicadas += 1
                    continue

                # Determina tipo da transação
                valor = abs(Decimal(str(transaction.amount)))
                tipo = 'RECEITA' if transaction.amount > 0 else 'DESPESA'

                # Tenta encontrar categoria baseada na descrição
                categoria = obter_categoria_automatica(
                    transaction.memo or transaction.payee or 'Sem descrição',
                    tipo,
                    usuario
                )

                # Cria a transação
                Transacao.objects.create(
                    descricao=transaction.memo or transaction.payee or 'Transação OFX',
                    valor=valor,
                    tipo=tipo,
                    data=transaction.date.date(),
                    categoria=categoria,
                    conta_bancaria=conta_bancaria,
                    usuario=usuario,
                    identificador_ofx=identificador,
                    importada_ofx=True
                )

                transacoes_importadas += 1

        # Atualiza registro de importação
        importacao.total_transacoes = total_transacoes
        importacao.transacoes_importadas = transacoes_importadas
        importacao.transacoes_duplicadas = transacoes_duplicadas
        importacao.save()

        return {
            'sucesso': True,
            'importadas': transacoes_importadas,
            'duplicadas': transacoes_duplicadas,
            'total': total_transacoes
        }

    except Exception as e:
        # Registra erro na importação
        ImportacaoOFX.objects.create(
            arquivo_nome=arquivo.name,
            usuario=usuario,
            sucesso=False,
            erro=str(e)
        )

        return {
            'sucesso': False,
            'erro': str(e)
        }


def obter_categoria_automatica(descricao, tipo, usuario):
    """
    Tenta associar automaticamente uma categoria baseada na descrição

    Args:
        descricao: Descrição da transação
        tipo: Tipo da transação (RECEITA/DESPESA)
        usuario: Usuário proprietário

    Returns:
        Categoria: Categoria encontrada ou categoria padrão
    """
    descricao_lower = descricao.lower()

    # Palavras-chave para categorização automática
    keywords = {
        'Alimentação': ['supermercado', 'mercado', 'padaria', 'restaurante', 'lanchonete', 'delivery', 'ifood'],
        'Transporte': ['combustivel', 'gasolina', 'uber', '99', 'taxi', 'onibus', 'metro', 'posto'],
        'Saúde': ['farmacia', 'hospital', 'clinica', 'medico', 'consulta', 'drogaria'],
        'Lazer': ['cinema', 'show', 'teatro', 'parque', 'viagem', 'netflix', 'spotify'],
        'Moradia': ['condominio', 'agua', 'luz', 'gas', 'telefone', 'internet', 'aluguel'],
        'Salário': ['salario', 'ordenado', 'pagamento', 'vencimento'],
        'Educação': ['escola', 'faculdade', 'curso', 'livro', 'material escolar'],
    }

    # Procura por palavras-chave na descrição
    for categoria_nome, palavras in keywords.items():
        for palavra in palavras:
            if palavra in descricao_lower:
                try:
                    categoria = Categoria.objects.get(
                        nome__iexact=categoria_nome,
                        tipo=tipo,
                        usuario=usuario,
                        ativa=True
                    )
                    return categoria
                except Categoria.DoesNotExist:
                    # Tenta buscar com nomes similares
                    try:
                        categoria = Categoria.objects.filter(
                            nome__icontains=categoria_nome.lower(),
                            tipo=tipo,
                            usuario=usuario,
                            ativa=True
                        ).first()
                        if categoria:
                            return categoria
                    except:
                        pass

    # Se não encontrou categoria específica, retorna ou cria categoria padrão
    if tipo == 'DESPESA':
        # Tenta encontrar uma categoria "Outros" existente primeiro
        try:
            categoria = Categoria.objects.get(
                nome__icontains='outros',
                tipo=tipo,
                usuario=usuario,
                ativa=True
            )
            return categoria
        except Categoria.DoesNotExist:
            pass

        categoria_padrao_nome = 'Outras Despesas'
    else:
        # Tenta encontrar uma categoria "Outros" existente primeiro
        try:
            categoria = Categoria.objects.get(
                nome__icontains='outros',
                tipo=tipo,
                usuario=usuario,
                ativa=True
            )
            return categoria
        except Categoria.DoesNotExist:
            pass

        categoria_padrao_nome = 'Outras Receitas'

    categoria, created = Categoria.objects.get_or_create(
        nome=categoria_padrao_nome,
        tipo=tipo,
        usuario=usuario,
        defaults={'ativa': True, 'cor': '#6c757d'}
    )

    return categoria
