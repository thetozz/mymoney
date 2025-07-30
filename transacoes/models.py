from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Categoria(models.Model):
    TIPOS_CATEGORIA = (
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    )

    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=7, choices=TIPOS_CATEGORIA)
    cor = models.CharField(max_length=7, default='#007bff',
                           help_text='Cor em formato hex (#ffffff)')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Categorias'
        unique_together = ['nome', 'usuario']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class ContaBancaria(models.Model):
    nome = models.CharField(max_length=100)
    banco = models.CharField(max_length=100)
    agencia = models.CharField(max_length=10, blank=True)
    conta = models.CharField(max_length=20, blank=True)
    saldo_inicial = models.DecimalField(
        max_digits=12, decimal_places=2, default=0)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ativa = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Contas Bancárias'
        unique_together = ['nome', 'usuario']

    def __str__(self):
        return f"{self.nome} - {self.banco}"

    def saldo_atual(self):
        from django.db.models import Sum
        receitas = self.transacao_set.filter(tipo='RECEITA').aggregate(
            total=Sum('valor'))['total'] or 0
        despesas = self.transacao_set.filter(tipo='DESPESA').aggregate(
            total=Sum('valor'))['total'] or 0
        return self.saldo_inicial + receitas - despesas


class Transacao(models.Model):
    TIPOS_TRANSACAO = (
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    )

    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=7, choices=TIPOS_TRANSACAO)
    data = models.DateField(default=timezone.now)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    conta_bancaria = models.ForeignKey(
        ContaBancaria, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    # Campos para controle de importação OFX
    identificador_ofx = models.CharField(
        max_length=100, blank=True, help_text='ID único do OFX para evitar duplicatas')
    importada_ofx = models.BooleanField(default=False)

    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Transações'
        ordering = ['-data', '-criado_em']
        indexes = [
            models.Index(fields=['usuario', 'data']),
            models.Index(fields=['usuario', 'tipo']),
            models.Index(fields=['identificador_ofx']),
        ]

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.get_tipo_display()})"


class TransacaoRecorrente(models.Model):
    TIPOS_RECORRENCIA = (
        ('MENSAL', 'Mensal'),
        ('BIMESTRAL', 'Bimestral'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    )
    
    TIPOS_TRANSACAO = (
        ('RECEITA', 'Receita'),
        ('DESPESA', 'Despesa'),
    )
    
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=12, decimal_places=2)
    tipo = models.CharField(max_length=7, choices=TIPOS_TRANSACAO)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    conta_bancaria = models.ForeignKey(ContaBancaria, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Configurações de recorrência
    tipo_recorrencia = models.CharField(max_length=11, choices=TIPOS_RECORRENCIA, default='MENSAL')
    dia_vencimento = models.IntegerField(default=1, help_text='Dia do mês (1-31)')
    data_inicio = models.DateField(default=timezone.now)
    data_fim = models.DateField(null=True, blank=True, help_text='Deixe vazio para recorrência indefinida')
    ativa = models.BooleanField(default=True)
    
    # Campos de auditoria
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Transações Recorrentes'
        ordering = ['tipo', 'descricao']
    
    def __str__(self):
        return f"{self.descricao} - R$ {self.valor} ({self.get_tipo_display()}) - {self.get_tipo_recorrencia_display()}"
    
    def proxima_data_vencimento(self, data_referencia=None):
        """Calcula a próxima data de vencimento baseada na recorrência"""
        if not data_referencia:
            data_referencia = timezone.now().date()
        
        from dateutil.relativedelta import relativedelta
        import calendar
        
        # Calcula o próximo vencimento baseado no tipo de recorrência
        if self.tipo_recorrencia == 'MENSAL':
            proxima_data = data_referencia.replace(day=1) + relativedelta(months=1)
        elif self.tipo_recorrencia == 'BIMESTRAL':
            proxima_data = data_referencia.replace(day=1) + relativedelta(months=2)
        elif self.tipo_recorrencia == 'TRIMESTRAL':
            proxima_data = data_referencia.replace(day=1) + relativedelta(months=3)
        elif self.tipo_recorrencia == 'SEMESTRAL':
            proxima_data = data_referencia.replace(day=1) + relativedelta(months=6)
        elif self.tipo_recorrencia == 'ANUAL':
            proxima_data = data_referencia.replace(day=1) + relativedelta(years=1)
        else:
            proxima_data = data_referencia.replace(day=1) + relativedelta(months=1)
        
        # Ajusta para o dia de vencimento correto
        ultimo_dia_mes = calendar.monthrange(proxima_data.year, proxima_data.month)[1]
        dia_ajustado = min(self.dia_vencimento, ultimo_dia_mes)
        
        return proxima_data.replace(day=dia_ajustado)
    
    def gerar_transacao_mes(self, mes, ano):
        """Gera uma transação para o mês especificado se aplicável"""
        import calendar
        
        # Calcula a data de vencimento para o mês
        ultimo_dia_mes = calendar.monthrange(ano, mes)[1]
        dia_ajustado = min(self.dia_vencimento, ultimo_dia_mes)
        data_vencimento = timezone.datetime(ano, mes, dia_ajustado).date()
        
        # Verifica se está dentro do período de vigência
        if data_vencimento < self.data_inicio:
            return None
        
        if self.data_fim and data_vencimento > self.data_fim:
            return None
        
        # Verifica se já existe transação para este período
        identificador = f"recorrente_{self.id}_{mes}_{ano}"
        if Transacao.objects.filter(
            usuario=self.usuario,
            identificador_ofx=identificador
        ).exists():
            return None
        
        # Cria a transação
        transacao = Transacao(
            descricao=f"{self.descricao} (Recorrente)",
            valor=self.valor,
            tipo=self.tipo,
            data=data_vencimento,
            categoria=self.categoria,
            conta_bancaria=self.conta_bancaria,
            usuario=self.usuario,
            identificador_ofx=identificador,
            importada_ofx=False
        )
        
        return transacao


class ImportacaoOFX(models.Model):
    arquivo_nome = models.CharField(max_length=255)
    data_importacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total_transacoes = models.IntegerField(default=0)
    transacoes_importadas = models.IntegerField(default=0)
    transacoes_duplicadas = models.IntegerField(default=0)
    sucesso = models.BooleanField(default=True)
    erro = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Importações OFX'
        ordering = ['-data_importacao']

    def __str__(self):
        return f"Importação {self.arquivo_nome} - {self.data_importacao.strftime('%d/%m/%Y %H:%M')}"
