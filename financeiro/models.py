from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError

# Create your models here.

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # 1. Pegar a margem (ex: 30%) e transformar em número decimal (0.30)
        fator = 1 + (self.margem_lucro / 100)

        # 2. Calcular o preço de venda multipicando o custo pelo fator
        self.preco_venda = self.preco_custo * fator

        # 3. Mandar o Django salvar de verdade no bancio de dados 
        super().save(*args, **kwargs)

class Venda(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveBigIntegerField()
    total_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    lucro_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        # TRAVA DE ESTOQUE:
        if self.quantidade > self.produto.estoque_atual:
            raise ValidationError(
                f"Estoque insuficiente! Você tentou vender {self.quantidade} unidades, "
                f"mas o produto '{self.produto.nome}' só tem {self.produto.estoque_atual} em estoque."
            )

        # 1. Primeiro, calculamos o valor bruto da venda (sem desconto nenhum)
        valor_bruto = self.quantidade * self.produto.preco_venda

        # 2. Criamos uma variável para guardar a porcentagem de desconto
        desconto_percentual = 0

        # 3. Aplicamos a regra de quantidade usando IF e ELIF
        if self.quantidade >= 10:
            desconto_percentual = 10 # 10% de desconto
        elif self.quantidade >= 5:
            desconto_percentual = 5 # 5% de desconto

        # 4. Calculamos o valor do desconto em dinheiro
        # Ex: se o bruto for 100 reais e o descoto for 5%, da 5 reais
        valor_do_desconto = valor_bruto * Decimal(desconto_percentual / 100)

        # 5. O total da venda agora será o valor bruto menos o desconto calculado
        self.total_venda = valor_bruto - valor_do_desconto

        # 6.Calculamos o lucro real tirando o custo do produto 
        custo_total = self.quantidade * self.produto.preco_custo
        self.lucro_venda = self.total_venda - custo_total

        # Deduz a quantidade de vendida do estoque do produto
        self.produto.estoque_atual -= self.quantidade
        self.produto.save() # Salva o novo estoque na tabela de Produtos 

        # 7. Salvamos no banco
        super().save(*args, **kwargs)

        def __str__(self):
            return f"Venda #{self.id} - {self.produto.nome}"

        