from django.contrib import admin
from .models import Produto, Venda

# Register your models here.

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_custo', 'margem_lucro', 'preco_venda', 'estoque_atual')
    readonly_fields = ('preco_venda',)

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'quantidade', 'total_venda', 'lucro_venda')
    readonly_fields = ('total_venda', 'lucro_venda') 
