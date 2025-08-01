"""
Serviço para integração com ChatGPT para categorização de transações
"""
import json
import logging
from django.conf import settings
from .models import Categoria

logger = logging.getLogger(__name__)

# Importação condicional do OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning(
        "OpenAI library not installed. ChatGPT integration disabled.")


def categorizar_transacoes_chatgpt(transacoes, usuario):
    """
    Usa ChatGPT para melhorar a categorização das transações

    Args:
        transacoes: Lista de transações para categorizar
        usuario: Usuário proprietário das transações

    Returns:
        list: Lista de transações com categorias melhoradas
    """
    # Busca todas as categorias do usuário para referência
    categorias_usuario = list(Categoria.objects.filter(
        usuario=usuario,
        ativa=True
    ).values('id', 'nome', 'tipo', 'cor'))

    # Verifica se ChatGPT está habilitado e disponível
    if (settings.CHATGPT_ENABLED and OPENAI_AVAILABLE and
            settings.OPENAI_API_KEY):
        try:
            transacoes = categorizar_com_chatgpt_real(
                transacoes, categorias_usuario)
            logger.info(
                f"ChatGPT categorization completed for {len(transacoes)} transactions")
        except Exception as e:
            logger.error(f"ChatGPT categorization failed: {str(e)}")
            # Fallback para categorização local
            transacoes = categorizar_com_regras_locais(
                transacoes, categorias_usuario)
    else:
        # Usa categorização local melhorada
        transacoes = categorizar_com_regras_locais(
            transacoes, categorias_usuario)

    return transacoes


def categorizar_com_chatgpt_real(transacoes, categorias_usuario):
    """
    Implementação real da categorização usando ChatGPT
    """
    # Configura o cliente OpenAI
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

    # Prepara dados para o ChatGPT
    categorias_por_tipo = {}
    for cat in categorias_usuario:
        tipo = cat['tipo']
        if tipo not in categorias_por_tipo:
            categorias_por_tipo[tipo] = []
        categorias_por_tipo[tipo].append({
            'id': cat['id'],
            'nome': cat['nome']
        })

    # Processa transações em lotes (máximo 10 por vez)
    batch_size = 10
    transacoes_processadas = []

    for i in range(0, len(transacoes), batch_size):
        batch = transacoes[i:i + batch_size]

        # Prepara prompt para o lote
        prompt = criar_prompt_categorizacao(batch, categorias_por_tipo)

        try:
            # Chama ChatGPT
            response = client.chat.completions.create(
                model=settings.CHATGPT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente especializado em categorização de transações financeiras. Analise cada transação e sugira a categoria mais apropriada baseada na descrição e no tipo (receita/despesa)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=settings.CHATGPT_MAX_TOKENS,
                temperature=settings.CHATGPT_TEMPERATURE,
                response_format={"type": "json_object"}
            )

            # Processa resposta
            resultado = json.loads(response.choices[0].message.content)
            batch_processado = aplicar_categorizacao_chatgpt(
                batch, resultado, categorias_usuario)
            transacoes_processadas.extend(batch_processado)

        except Exception as e:
            logger.error(
                f"Error processing batch {i//batch_size + 1}: {str(e)}")
            # Fallback para regras locais neste lote
            batch_local = categorizar_com_regras_locais(
                batch, categorias_usuario)
            transacoes_processadas.extend(batch_local)

    return transacoes_processadas


def criar_prompt_categorizacao(transacoes, categorias_por_tipo):
    """
    Cria o prompt para enviar ao ChatGPT
    """
    prompt = """
Analise as seguintes transações financeiras e sugira a categoria mais apropriada para cada uma.

CATEGORIAS DISPONÍVEIS:
"""

    for tipo, categorias in categorias_por_tipo.items():
        prompt += f"\n{tipo}:\n"
        for cat in categorias:
            prompt += f"  - {cat['nome']} (ID: {cat['id']})\n"

    prompt += "\nTRANSAÇÕES PARA CATEGORIZAR:\n"

    for i, transacao in enumerate(transacoes):
        prompt += f"{i+1}. Descrição: '{transacao['descricao']}', Tipo: {transacao['tipo']}, Valor: R$ {transacao['valor']:.2f}\n"

    prompt += """
INSTRUÇÕES:
- Para cada transação, retorne apenas o ID da categoria mais apropriada
- Se não houver categoria adequada, retorne null
- Considere o contexto brasileiro (nomes de empresas, bancos, etc.)
- Seja preciso na categorização baseada na descrição

Responda no formato JSON:
{
  "categorizacoes": [
    {"transacao_index": 0, "categoria_id": 123, "confianca": 0.95},
    {"transacao_index": 1, "categoria_id": null, "confianca": 0.0}
  ]
}
"""

    return prompt


def aplicar_categorizacao_chatgpt(transacoes, resultado_chatgpt, categorias_usuario):
    """
    Aplica as categorizações sugeridas pelo ChatGPT
    """
    # Cria mapa de categorias por ID para busca rápida
    categorias_map = {cat['id']: cat for cat in categorias_usuario}

    # Aplica categorizações
    for item in resultado_chatgpt.get('categorizacoes', []):
        try:
            idx = item['transacao_index']
            categoria_id = item['categoria_id']
            confianca = item.get('confianca', 0.0)

            if 0 <= idx < len(transacoes) and categoria_id in categorias_map:
                categoria = categorias_map[categoria_id]
                transacoes[idx]['categoria_id'] = categoria['id']
                transacoes[idx]['categoria_nome'] = categoria['nome']
                transacoes[idx]['categoria_cor'] = categoria['cor']
                transacoes[idx]['melhorada_chatgpt'] = True
                transacoes[idx]['confianca_ia'] = confianca
            else:
                # Mantém categoria original se não encontrou sugestão válida
                transacoes[idx]['melhorada_chatgpt'] = False
                transacoes[idx]['confianca_ia'] = 0.0

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error applying ChatGPT categorization: {str(e)}")
            continue

    return transacoes


def categorizar_com_regras_locais(transacoes, categorias_usuario):
    """
    Categorização usando regras locais melhoradas (fallback)
    """
    for transacao in transacoes:
        transacao = melhorar_categorizacao_local(transacao, categorias_usuario)

    return transacoes


def melhorar_categorizacao_local(transacao, categorias_usuario):
    """
    Aplica regras locais melhoradas para categorização
    """
    descricao = transacao['descricao'].lower()
    tipo = transacao['tipo']

    # Regras específicas melhoradas
    regras_melhoradas = {
        'DESPESA': {
            'mercado': ['supermercado', 'mercado', 'emporio', 'atacadao', 'extra', 'carrefour', 'pao de acucar'],
            'combustivel': ['posto', 'gasolina', 'etanol', 'diesel', 'shell', 'petrobras', 'ipiranga'],
            'farmacia': ['farmacia', 'drogaria', 'drogasil', 'pacheco', 'ultrafarma'],
            'restaurante': ['restaurante', 'lanchonete', 'pizzaria', 'hamburger', 'mcdonald', 'burger king'],
            'transporte': ['uber', '99', 'taxi', 'onibus', 'metro', 'trem', 'pedagio'],
            'saude': ['hospital', 'clinica', 'laboratorio', 'exame', 'consulta', 'medico'],
            'educacao': ['escola', 'faculdade', 'universidade', 'curso', 'aula', 'mensalidade'],
            'lazer': ['cinema', 'teatro', 'show', 'parque', 'netflix', 'spotify', 'amazon prime'],
            'moradia': ['condominio', 'aluguel', 'iptu', 'agua', 'luz', 'gas', 'internet', 'telefone'],
            'vestuario': ['loja', 'roupa', 'calcado', 'sapato', 'tenis', 'camisa', 'vestido'],
            'tecnologia': ['informatica', 'computador', 'celular', 'tablet', 'software', 'hardware']
        },
        'RECEITA': {
            'salario': ['salario', 'ordenado', 'pagamento', 'vencimento', 'folha'],
            'freelance': ['freelance', 'consultoria', 'servico', 'trabalho extra'],
            'investimento': ['dividendo', 'juros', 'rendimento', 'aplicacao', 'poupanca'],
            'venda': ['venda', 'comissao', 'bonificacao', 'premio']
        }
    }

    # Tenta encontrar melhor categoria baseada nas regras
    if tipo in regras_melhoradas:
        for categoria_chave, palavras_chave in regras_melhoradas[tipo].items():
            for palavra in palavras_chave:
                if palavra in descricao:
                    # Procura categoria correspondente do usuário
                    for cat in categorias_usuario:
                        if (categoria_chave.lower() in cat['nome'].lower() or
                                cat['nome'].lower() in categoria_chave.lower()) and cat['tipo'] == tipo:
                            transacao['categoria_id'] = cat['id']
                            transacao['categoria_nome'] = cat['nome']
                            transacao['categoria_cor'] = cat['cor']
                            transacao['melhorada_chatgpt'] = True
                            return transacao

    # Adiciona flag indicando que não foi melhorada
    transacao['melhorada_chatgpt'] = False
    return transacao


def implementar_chatgpt_real():
    """
    TODO: Implementar integração real com ChatGPT

    Passos futuros:
    1. Configurar API key do OpenAI
    2. Criar prompt otimizado para categorização
    3. Enviar lote de transações para análise
    4. Processar resposta e aplicar categorizações
    5. Implementar cache para evitar re-processar mesmas transações
    """
    pass
