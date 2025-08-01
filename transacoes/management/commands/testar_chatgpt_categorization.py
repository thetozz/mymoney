"""
Comando para testar a integração com ChatGPT
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from transacoes.chatgpt_service import categorizar_transacoes_chatgpt
from transacoes.models import Categoria


class Command(BaseCommand):
    help = 'Testa a integração com ChatGPT para categorização de transações'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario-id',
            type=int,
            default=1,
            help='ID do usuário para testar (padrão: 1)'
        )

    def handle(self, *args, **options):
        usuario_id = options['usuario_id']

        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário com ID {usuario_id} não encontrado')
            )
            return

        # Verifica configuração
        self.stdout.write('=== TESTE DE INTEGRAÇÃO CHATGPT ===')
        self.stdout.write(f'ChatGPT Habilitado: {settings.CHATGPT_ENABLED}')
        self.stdout.write(
            f'API Key configurada: {"Sim" if settings.OPENAI_API_KEY else "Não"}')
        self.stdout.write(f'Modelo: {settings.CHATGPT_MODEL}')
        self.stdout.write('')

        # Cria transações de teste
        transacoes_teste = [
            {
                'descricao': 'SUPERMERCADO EXTRA',
                'valor': 89.50,
                'tipo': 'DESPESA',
                'data': '2024-08-01',
                'categoria_id': 1,
                'categoria_nome': 'Outras Despesas',
                'categoria_cor': '#6c757d'
            },
            {
                'descricao': 'POSTO SHELL GASOLINA',
                'valor': 120.00,
                'tipo': 'DESPESA',
                'data': '2024-08-01',
                'categoria_id': 1,
                'categoria_nome': 'Outras Despesas',
                'categoria_cor': '#6c757d'
            },
            {
                'descricao': 'SALARIO EMPRESA XYZ',
                'valor': 3500.00,
                'tipo': 'RECEITA',
                'data': '2024-08-01',
                'categoria_id': 2,
                'categoria_nome': 'Outras Receitas',
                'categoria_cor': '#28a745'
            },
            {
                'descricao': 'UBER TRIP',
                'valor': 25.50,
                'tipo': 'DESPESA',
                'data': '2024-08-01',
                'categoria_id': 1,
                'categoria_nome': 'Outras Despesas',
                'categoria_cor': '#6c757d'
            }
        ]

        self.stdout.write('=== TRANSAÇÕES DE TESTE ===')
        for i, t in enumerate(transacoes_teste, 1):
            self.stdout.write(
                f'{i}. {t["descricao"]} - R$ {t["valor"]:.2f} ({t["tipo"]})')

        self.stdout.write('')
        self.stdout.write('=== CATEGORIAS DISPONÍVEIS ===')
        categorias = Categoria.objects.filter(usuario=usuario, ativa=True)
        for cat in categorias:
            self.stdout.write(f'- {cat.nome} ({cat.tipo}) [ID: {cat.id}]')

        self.stdout.write('')
        self.stdout.write('=== INICIANDO CATEGORIZAÇÃO ===')

        try:
            # Testa categorização
            resultado = categorizar_transacoes_chatgpt(
                transacoes_teste, usuario)

            self.stdout.write('=== RESULTADO ===')
            for i, transacao in enumerate(resultado, 1):
                melhorada = transacao.get('melhorada_chatgpt', False)
                confianca = transacao.get('confianca_ia', 0)
                status = '🤖 ChatGPT' if melhorada else '⚙️ Local'

                self.stdout.write(
                    f'{i}. {transacao["descricao"][:30]}... → '
                    f'{transacao["categoria_nome"]} ({status}'
                    f'{f", {confianca:.0%}" if confianca > 0 else ""})'
                )

            self.stdout.write('')
            total_chatgpt = sum(1 for t in resultado if t.get(
                'melhorada_chatgpt', False))
            total_local = len(resultado) - total_chatgpt

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Teste concluído! '
                    f'ChatGPT: {total_chatgpt}, Local: {total_local}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro durante o teste: {str(e)}')
            )

        if not settings.CHATGPT_ENABLED:
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING(
                    '⚠️ Para habilitar ChatGPT, configure OPENAI_API_KEY no arquivo .env'
                )
            )
