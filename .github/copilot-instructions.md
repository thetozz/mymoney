# Copilot Instructions - Sistema de Finanças Pessoais

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Contexto do Projeto
Este é um sistema web Django para controle de finanças pessoais com as seguintes características:

### Tecnologias
- Backend: Django Framework (Python)
- Frontend: HTML5 + Bootstrap 5
- Banco de dados: SQLite (desenvolvimento) / PostgreSQL (produção)

### Estrutura dos Apps
- **usuarios**: Autenticação de usuários (login, logout, registro)
- **transacoes**: Gerenciamento de receitas, despesas e importação de arquivos OFX
- **dashboard**: Visualização de dados, gráficos e relatórios

### Funcionalidades Principais
- Importação de arquivos .ofx bancários
- Cadastro de receitas, despesas e categorias
- Dashboard com gráficos (barras/pizza)
- Interface responsiva com Bootstrap 5
- Suporte a múltiplos usuários
- Fuso horário: America/Sao_Paulo
- Prevenção de duplicatas na importação

### Padrões de Código
- Use sempre timezone-aware datetime objects
- Implemente separação de dados por usuário
- Mantenha a interface limpa e responsiva
- Use class-based views do Django quando apropriado
- Siga as convenções PEP 8 para Python
