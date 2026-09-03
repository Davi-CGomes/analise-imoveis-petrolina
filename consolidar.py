import json
import csv
import os

from limpeza import (
    limpar_preco,
    limpar_area,
    limpar_int,
    normalizar_finalidade,
    normalizar_bairro,
)


# Carregamento 
with open("data/raw/a7_bruto.json", encoding="utf-8") as f:
    imoveis_a7 = json.load(f)

with open("data/raw/olx_venda_bruto.json", encoding="utf-8") as f:
    imoveis_olx = json.load(f)

todos = imoveis_olx + imoveis_a7
print(f"Carregados: {len(todos)} imóveis brutos")

# Mantém apenas os campos que existem nas duas fontes
COLUNAS = [
    'titulo', 'preco', 'bairro', 'area',
    'quartos', 'banheiros', 'vagas',
    'finalidade', 'fonte', 'link'
]

registros = []
for item in todos:
    registros.append({
        'titulo': item.get('titulo'),
        'preco': limpar_preco(item.get('preco')),
        'bairro': normalizar_bairro(item.get('bairro')),
        'area': limpar_area(item.get('area')),
        'quartos': limpar_int(item.get('quartos')),
        'banheiros': limpar_int(item.get('banheiros')),
        'vagas': limpar_int(item.get('vagas')),
        'finalidade': normalizar_finalidade(item.get('finalidade')),
        'fonte': item.get('fonte'),
        'link': item.get('link'),
    })

# Titulos podem se repetir entre imóveis, mas o link é o identificador confiável.
links_vistos = set()
unicos = []
for r in registros:
    if r['link'] not in links_vistos:
        links_vistos.add(r['link'])
        unicos.append(r)
print(f"Após deduplicar: {len(unicos)}")


# R$ 50 mil fica abaixo de qualquer imóvel de venda real em Petrolina, mas acima de aluguéis que aparecem na busca
PRECO_MINIMO = 50000
limpos = [r for r in unicos if r['preco'] and r['preco'] >= PRECO_MINIMO]
print(f"Após corte de R$ {PRECO_MINIMO:,}: {len(limpos)}")

# Escrita do CSV
caminho = "data/processed/imoveis_consolidado.csv"
os.makedirs(os.path.dirname(caminho), exist_ok=True)
with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=COLUNAS)
    writer.writeheader()
    writer.writerows(limpos)

print(f"Salvo: {len(limpos)} imóveis em {caminho}")