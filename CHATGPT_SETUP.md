# Configuração do ChatGPT para Categorização Inteligente

## Visão Geral

O sistema agora suporta categorização inteligente de transações usando ChatGPT da OpenAI. Quando habilitado, o ChatGPT analisa as descrições das transações e sugere categorias mais precisas baseadas no contexto.

## Como Configurar

### 1. Obter API Key do OpenAI

1. Acesse [OpenAI Platform](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá para [API Keys](https://platform.openai.com/api-keys)
4. Clique em "Create new secret key"
5. Copie a chave gerada (formato: `sk-proj-...`)

### 2. Configurar no Sistema

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .env.example .env
   ```

2. **Edite o arquivo `.env`:**
   ```bash
   nano .env
   ```

3. **Substitua `sua_api_key_aqui` pela sua API key:**
   ```env
   OPENAI_API_KEY=sk-proj-sua_api_key_real_aqui
   ```

4. **Reinicie o servidor Django:**
   ```bash
   python manage.py runserver
   ```

### 3. Testar a Configuração

Execute o comando de teste:
```bash
python manage.py testar_chatgpt_categorization --usuario-id=1
```

## Como Funciona

### Processo de Categorização

1. **Upload do arquivo OFX** → Sistema extrai transações
2. **Categorização inicial** → Aplica regras locais básicas
3. **Análise ChatGPT** → Envia lote de transações para análise
4. **Aplicação de sugestões** → Substitui categorias com melhor precisão
5. **Fallback inteligente** → Usa regras locais se ChatGPT falhar

### Indicadores Visuais

- 🤖 **Ícone de robô verde**: Categoria sugerida pelo ChatGPT
- ⚙️ **Ícone de engrenagem cinza**: Categoria por regras locais
- **Porcentagem de confiança**: Mostrada no tooltip (quando disponível)

### Configurações Avançadas

No arquivo `settings.py`, você pode ajustar:

```python
CHATGPT_MODEL = 'gpt-3.5-turbo'      # Modelo a usar
CHATGPT_MAX_TOKENS = 1000            # Máximo de tokens por resposta
CHATGPT_TEMPERATURE = 0.3            # Criatividade (0.0-1.0)
```

## Custos e Limites

### Custos da API OpenAI

- **GPT-3.5-turbo**: ~$0.0015 por 1K tokens de entrada + $0.002 por 1K tokens de saída
- **Estimativa**: ~$0.01-0.05 por 100 transações processadas
- **Otimização**: Sistema processa em lotes de 10 transações

### Controle de Custos

1. **Processamento em lotes**: Reduz número de chamadas
2. **Fallback automático**: Usa regras locais em caso de erro
3. **Cache inteligente**: Evita reprocessar mesmas transações
4. **Tokens otimizados**: Prompts concisos e estruturados

## Troubleshooting

### Problemas Comuns

**1. ChatGPT não está ativando**
```bash
# Verificar configuração
python manage.py testar_chatgpt_categorization

# Verificar variável de ambiente
echo $OPENAI_API_KEY
```

**2. Erro de API Key inválida**
- Verifique se a key está correta no arquivo `.env`
- Confirme que a key tem créditos disponíveis
- Teste a key em [OpenAI Playground](https://platform.openai.com/playground)

**3. Transações usando regras locais**
- Verifique se há saldo na conta OpenAI
- Veja logs do Django para erros específicos
- Sistema faz fallback automático para regras locais

**4. Erro de importação OpenAI**
```bash
# Reinstalar biblioteca
pip install --upgrade openai
```

### Logs e Debug

Para debug detalhado, adicione no `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'transacoes.chatgpt_service': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Monitoramento de Uso

### Dashboard OpenAI

1. Acesse [Usage Dashboard](https://platform.openai.com/usage)
2. Monitore consumo de tokens
3. Configure alertas de limite de gastos

### Métricas do Sistema

O sistema registra:
- Número de transações processadas por ChatGPT vs regras locais
- Taxa de sucesso das chamadas API
- Tempo médio de processamento
- Categorias mais frequentemente sugeridas

## Segurança

### Boas Práticas

1. **Nunca versione a API key** (arquivo `.env` no `.gitignore`)
2. **Use variáveis de ambiente** para credenciais
3. **Monitore uso irregular** no dashboard OpenAI
4. **Rotacione keys periodicamente**

### Dados Enviados

O ChatGPT recebe apenas:
- Descrição da transação
- Tipo (receita/despesa)
- Valor
- Lista de categorias disponíveis

**Não são enviados:**
- Dados pessoais do usuário
- Informações da conta bancária
- Histórico de transações
- Outros dados sensíveis

## Benefícios vs Regras Locais

### ChatGPT
✅ Maior precisão na categorização  
✅ Entende contexto e variações  
✅ Aprende com padrões complexos  
✅ Suporte a nomes de empresas variados  
❌ Requer API key e gera custos  
❌ Dependente de conexão internet  

### Regras Locais
✅ Gratuito e sempre disponível  
✅ Rápido e sem dependências  
✅ Funciona offline  
❌ Precisão limitada  
❌ Requer manutenção manual das regras  

O sistema usa **ChatGPT quando disponível** e faz **fallback inteligente** para regras locais quando necessário, garantindo que a importação sempre funcione independente da configuração.
