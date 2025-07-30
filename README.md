# Sistema de Finanças Pessoais

Um sistema web completo para controle de finanças pessoais desenvolvido com Django Framework e Bootstrap 5.

## 🚀 Funcionalidades

### 📊 Dashboard
- Resumo financeiro com receitas, despesas e saldo
- Gráficos de pizza mostrando distribuição por categoria
- Filtros por período (mês/ano)
- Transações recentes
- Interface responsiva com Bootstrap 5

### 💰 Gestão de Transações
- Cadastro de receitas e despesas
- Categorização com cores personalizadas
- Filtros avançados por tipo, categoria e busca textual
- Paginação para grandes volumes de dados

### 📁 Importação de Arquivos OFX
- Importação de extratos bancários em formato OFX
- Detecção automática de duplicatas
- Associação automática com categorias conhecidas
- Histórico de importações

### 👥 Sistema de Usuários
- Autenticação completa (login, logout, registro)
- Dados separados por usuário
- Interface de administração Django

### 🏷️ Categorias
- Categorias personalizáveis para receitas e despesas
- Cores customizadas para melhor visualização
- Categorias padrão pré-configuradas

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.2 (Python)
- **Frontend**: HTML5, Bootstrap 5, Chart.js
- **Banco de Dados**: SQLite (desenvolvimento)
- **Processamento OFX**: ofxparse
- **Timezone**: America/Sao_Paulo

## 📋 Pré-requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

## 🔧 Instalação e Configuração

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd finance
```

### 2. Ative o ambiente virtual
```bash
# O ambiente virtual já está configurado em .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install django ofxparse pillow python-decouple pytz
```

### 4. Execute as migrações
```bash
python manage.py migrate
```

### 5. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 6. Execute o servidor de desenvolvimento
```bash
python manage.py runserver
```

### 7. Acesse o sistema
- Aplicação: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## 📁 Estrutura do Projeto

```
finance/
├── finance_system/          # Configurações do Django
├── usuarios/                # App de autenticação
├── transacoes/             # App de transações e OFX
├── dashboard/              # App de visualização
├── templates/              # Templates HTML
├── static/                 # Arquivos estáticos
├── media/                  # Upload de arquivos
└── manage.py
```

## 🎯 Como Usar

### Primeiro Acesso
1. Registre uma nova conta ou faça login
2. Crie categorias básicas (ou use o comando de categorias padrão)
3. Adicione suas primeiras transações manualmente
4. Ou importe um arquivo OFX do seu banco

### Importação OFX
1. Baixe o extrato OFX do site do seu banco
2. Acesse "Importar OFX" no menu
3. Selecione o arquivo e uma conta (opcional)
4. As transações serão importadas automaticamente

### Categorias Padrão
Para criar categorias padrão para um usuário:
```bash
python manage.py criar_categorias_padrao --user SEU_USERNAME
```

## 🔐 Segurança

- Dados separados por usuário
- Autenticação obrigatória para todas as funcionalidades
- Proteção CSRF em todos os formulários
- Validação de dados no backend

## 🌐 Responsividade

O sistema é totalmente responsivo e funciona bem em:
- Desktops
- Tablets
- Smartphones

## 📈 Funcionalidades Avançadas

### Gráficos Interativos
- Chart.js para visualizações dinâmicas
- Gráficos de pizza para distribuição por categoria
- Cores personalizadas baseadas nas categorias

### Filtros Avançados
- Filtros por período no dashboard
- Busca textual nas transações
- Filtros por tipo e categoria

### Prevenção de Duplicatas
- Sistema inteligente que detecta transações duplicadas na importação OFX
- Baseado em ID único, data e valor da transação

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Se você encontrar algum problema ou tiver dúvidas:
1. Verifique a documentação
2. Procure em issues existentes
3. Crie uma nova issue com detalhes do problema

## ✅ Sistema Pronto para Uso

O sistema está **completamente funcional** e pronto para uso! Aqui está um resumo do que foi criado:

### 🎯 Funcionalidades Implementadas

✅ **Sistema de Autenticação Completo**
- Login e logout de usuários
- Registro de novos usuários
- Proteção de rotas autenticadas

✅ **Dashboard Interativo**
- Cards com resumo financeiro (receitas, despesas, saldo)
- Gráficos de pizza por categoria (Chart.js)
- Filtros por mês/ano
- Transações recentes

✅ **Gestão de Transações**
- CRUD completo (criar, listar, editar, excluir)
- Filtros por tipo, categoria e busca textual
- Paginação para performance
- Validações de formulário

✅ **Sistema de Categorias**
- Criação de categorias personalizadas
- Cores customizáveis
- Separação por tipo (receita/despesa)
- Categorias padrão pré-configuradas

✅ **Importação de Arquivos OFX**
- Upload e processamento de extratos bancários
- Detecção automática de duplicatas
- Categorização automática inteligente
- Histórico de importações

✅ **Interface Responsiva**
- Design moderno com Bootstrap 5
- Totalmente responsivo para mobile
- Ícones Bootstrap Icons
- Cores e temas consistentes

✅ **Funcionalidades Avançadas**
- Separação de dados por usuário
- Timezone configurado para Brasil
- Admin Django configurado
- Validações e segurança

### 🚀 Como Usar Agora

1. **Faça login com:** 
   - Usuário: `admin`
   - Senha: `123` (ou a que você definiu)

2. **Acesse:** http://127.0.0.1:8000

3. **O sistema já tem:**
   - Categorias padrão criadas
   - Interface completa funcionando
   - Todas as funcionalidades ativas

### 📱 Próximos Passos Sugeridos

1. **Crie suas primeiras transações** manualmente
2. **Teste a importação OFX** com um arquivo do seu banco
3. **Explore o dashboard** e filtros
4. **Customize as categorias** conforme sua necessidade
5. **Crie outros usuários** para testar a separação de dados

### 🎉 Sistema 100% Funcional!

Este é um sistema de finanças pessoais **completo e profissional**, seguindo as melhores práticas de desenvolvimento Django. Todas as funcionalidades solicitadas foram implementadas com sucesso!
