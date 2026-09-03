import json
from collections import Counter

from limpeza import limpar_preco, limpar_area, normalizar_bairro


# Carregamento dos dados brutos
with open("data/raw/a7_bruto.json", encoding="utf-8") as f:
    imoveis_a7 = json.load(f)

with open("data/raw/olx_venda_bruto.json", encoding="utf-8") as f:
    imoveis_olx = json.load(f)

todos = imoveis_olx + imoveis_a7
contagem = Counter(i['bairro'] for i in todos if i['bairro'])

# Comparar as duas contagens revela quantos bairros estavam duplicados
contagem_norm = Counter(normalizar_bairro(i['bairro']) for i in todos if i['bairro'])

print(f"Total de imóveis: {len(todos)}")
print(f"Bairros antes de normalizar: {len(contagem)}")
print(f"Bairros depois de normalizar: {len(contagem_norm)}\n")

for bairro, qtd in contagem_norm.most_common():
    print(f"{qtd:4} — {bairro}")


# Conversão de preço e área para número
for item in todos:
    item['preco_num'] = limpar_preco(item['preco'])
    item['area_num'] = limpar_area(item['area'])

print(f"Total: {len(todos)}")
print(f"Com preço numérico: {sum(1 for i in todos if i['preco_num'])}")
print(f"Com área numérica: {sum(1 for i in todos if i['area_num'])}")
print(f"Com ambos (permite preço/m²): {sum(1 for i in todos if i['preco_num'] and i['area_num'])}")

# Os valores nas pontas expõem dado sujo que a média esconde, anúncios de aluguel
precos = sorted([i['preco_num'] for i in todos if i['preco_num']])
print(f"Menor preço: R$ {precos[0]:,.2f}")
print(f"Maior preço: R$ {precos[-1]:,.2f}")
print(f"Mediana: R$ {precos[len(precos)//2]:,.2f}")

print("\n5 mais baratos:")
for i in sorted([x for x in todos if x['preco_num']], key=lambda x: x['preco_num'])[:5]:
    print(f"  R$ {i['preco_num']:,.2f} — {i['titulo'][:50]} ({i['fonte']})")

print("\n5 mais caros:")
for i in sorted([x for x in todos if x['preco_num']], key=lambda x: -x['preco_num'])[:5]:
    print(f"  R$ {i['preco_num']:,.2f} — {i['titulo'][:50]} ({i['fonte']})")

# Verifica se a ausência de área se concentra em uma das fontes
sem_area = [i for i in todos if not i['area_num']]
print(Counter(i['fonte'] for i in sem_area))

# Títulos podem se repetir entre imóveis
links_vistos = set()
todos_unicos = []
for item in todos:
    if item['link'] not in links_vistos:
        links_vistos.add(item['link'])
        todos_unicos.append(item)

print(f"Antes de deduplicar: {len(todos)}")
print(f"Depois de deduplicar: {len(todos_unicos)}")

# R$ 50 mil fica abaixo de qualquer imóvel de venda real em Petrolina, mas acima de aluguéis que aparecem na busca
PRECO_MINIMO = 50000
antes = len(todos_unicos)
todos_limpos = [i for i in todos_unicos if i['preco_num'] and i['preco_num'] >= PRECO_MINIMO]
print(f"Removidos por preço abaixo de R$ {PRECO_MINIMO:,}: {antes - len(todos_limpos)}")
print(f"Restam: {len(todos_limpos)}")