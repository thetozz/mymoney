from django import forms
from .models import Transacao, Categoria, ContaBancaria, TransacaoRecorrente


class TransacaoForm(forms.ModelForm):
    class Meta:
        model = Transacao
        fields = ['descricao', 'valor', 'tipo',
                  'data', 'categoria', 'conta_bancaria']
        widgets = {
            'data': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'descricao': 'Descrição',
            'conta_bancaria': 'Conta Bancária (opcional)',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar o formato de entrada para o campo data
        self.fields['data'].input_formats = ['%Y-%m-%d']

        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                usuario=user, ativa=True
            )
            self.fields['conta_bancaria'].queryset = ContaBancaria.objects.filter(
                usuario=user, ativa=True
            )
            self.fields['conta_bancaria'].empty_label = "Selecione uma conta (opcional)"


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'tipo', 'cor']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }


class ContaBancariaForm(forms.ModelForm):
    class Meta:
        model = ContaBancaria
        fields = ['nome', 'banco', 'agencia', 'conta', 'saldo_inicial']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'agencia': forms.TextInput(attrs={'class': 'form-control'}),
            'conta': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo_inicial': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'saldo_inicial': 'Saldo Inicial',
        }


class TransacaoRecorrenteForm(forms.ModelForm):
    class Meta:
        model = TransacaoRecorrente
        fields = [
            'descricao', 'valor', 'tipo', 'data_inicio', 'data_fim',
            'categoria', 'conta_bancaria', 'tipo_recorrencia', 'dia_vencimento',
            'ativa'
        ]
        widgets = {
            'data_inicio': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'data_fim': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'descricao': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ex: Salário, Aluguel, Energia Elétrica'
                }
            ),
            'valor': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01'}
            ),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'conta_bancaria': forms.Select(attrs={'class': 'form-select'}),
            'tipo_recorrencia': forms.Select(attrs={'class': 'form-select'}),
            'dia_vencimento': forms.NumberInput(
                attrs={'class': 'form-control', 'min': '1', 'max': '31'}
            ),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'descricao': 'Descrição',
            'data_inicio': 'Data de Início',
            'data_fim': 'Data de Fim (opcional)',
            'conta_bancaria': 'Conta Bancária (opcional)',
            'tipo_recorrencia': 'Tipo de Recorrência',
            'dia_vencimento': 'Dia do Vencimento',
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                usuario=user, ativa=True
            )
            self.fields['conta_bancaria'].queryset = (
                ContaBancaria.objects.filter(usuario=user, ativa=True)
            )
            self.fields['conta_bancaria'].empty_label = (
                "Selecione uma conta (opcional)"
            )

        # Configuração adicional para campos específicos
        self.fields['data_fim'].required = False
        self.fields['ativa'].initial = True

        # Help texts personalizados
        self.fields['dia_vencimento'].help_text = (
            "Dia do mês para gerar a transação (1-31)"
        )
        self.fields['data_fim'].help_text = (
            "Deixe vazio para recorrência indefinida"
        )

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        dia_vencimento = cleaned_data.get('dia_vencimento')

        # Validar se data_fim é posterior a data_inicio
        if data_inicio and data_fim and data_fim <= data_inicio:
            raise forms.ValidationError(
                "A data de fim deve ser posterior à data de início."
            )

        # Validar dia_vencimento
        if dia_vencimento:
            if dia_vencimento < 1 or dia_vencimento > 31:
                raise forms.ValidationError(
                    "Dia de vencimento deve estar entre 1 e 31."
                )

        return cleaned_data
