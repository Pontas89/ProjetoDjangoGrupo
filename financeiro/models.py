from django.db import models

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
        # 1. Multiplica a quantidade digitada pelo preço de venda do produto vinculado
        self.total_venda = self.quantidade * self.produto.preco_venda

        # 2. Calcula o custo total daqueles itens para a loja
        custo_total = self.quantidade * self.produto.preco_custo

        # 3. Calcula o lucro líquido (O total que entrou menos o que os produtos custaram)
        self.lucro_venda = self.total_venda - custo_total

        # 4. Finaliza salvando no banco
        super().save(*args, **kwargs)

        