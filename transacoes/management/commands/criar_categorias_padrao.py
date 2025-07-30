from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transacoes.models import Categoria


class Command(BaseCommand):
    help = 'Cria categorias padrão para um usuário'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username do usuário')

    def handle(self, *args, **options):
        username = options.get('user')

        if not username:
            self.stdout.write(
                self.style.ERROR(
                    'Por favor, especifique um usuário com --user')
            )
            return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário "{username}" não encontrado')
            )
            return

        # Categorias de receita
        receitas = [
            ('Salário', '#28a745'),
            ('Freelance', '#20c997'),
            ('Investimentos', '#17a2b8'),
            ('Outros', '#6c757d'),
        ]

        # Categorias de despesa
        despesas = [
            ('Alimentação', '#dc3545'),
            ('Transporte', '#fd7e14'),
            ('Moradia', '#6f42c1'),
            ('Saúde', '#e83e8c'),
            ('Educação', '#007bff'),
            ('Lazer', '#ffc107'),
            ('Roupas', '#198754'),
            ('Outras Despesas', '#6c757d'),
        ]

        created_count = 0

        # Criar categorias de receita
        for nome, cor in receitas:
            categoria, created = Categoria.objects.get_or_create(
                nome=nome,
                tipo='RECEITA',
                usuario=user,
                defaults={'cor': cor, 'ativa': True}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Categoria criada: {nome} (Receita)')

        # Criar categorias de despesa
        for nome, cor in despesas:
            categoria, created = Categoria.objects.get_or_create(
                nome=nome,
                tipo='DESPESA',
                usuario=user,
                defaults={'cor': cor, 'ativa': True}
            )
            if created:
                created_count += 1
                self.stdout.write(f'Categoria criada: {nome} (Despesa)')

        self.stdout.write(
            self.style.SUCCESS(
                f'Comando concluído! {created_count} categorias criadas para {username}'
            )
        )
