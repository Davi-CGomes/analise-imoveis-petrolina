import requests
from bs4 import BeautifulSoup
import json
import time
import os


def parse_card(text_div):
    """Extrai os dados de um card a partir da div.pi-text"""
    
    # Preço
    preco_tag = text_div.select_one('.pt-price')
    preco = preco_tag.get_text(strip=True) if preco_tag else None

    # Título / link do imóvel
    titulo_tag = text_div.select_one('h5 a')
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None
    link = titulo_tag['href'] if titulo_tag else None

    # Área, banheiros, quartos, vagas
    li_tags = text_div.select('ul li')
    area = li_tags[0].get_text(strip=True) if len(li_tags) > 0 else None
    banheiros = li_tags[1].get_text(strip=True) if len(li_tags) > 1 else None
    quartos = li_tags[2].get_text(strip=True) if len(li_tags) > 2 else None
    vagas = li_tags[3].get_text(strip=True) if len(li_tags) > 3 else None

    # Bairro
    bairro_tag = text_div.select_one('p')
    bairro = bairro_tag.get_text(strip=True) if bairro_tag else None

    # Finalidade (Venda/Aluguel) — está no <a> irmão anterior
    label = None
    prev_a = text_div.find_previous_sibling('a')
    if prev_a:
        label_tag = prev_a.select_one('.label')
        if label_tag:
            label = label_tag.get_text(strip=True)

    return {
        'titulo': titulo,
        'preco': preco,
        'bairro': bairro,
        'area': area,
        'banheiros': banheiros,
        'quartos': quartos,
        'vagas': vagas,
        'finalidade': label,
        'link': link,
        'fonte': 'A7 Imobiliaria'
    }


def scrape_pagina(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.select('div.pi-text')
    return [parse_card(c) for c in cards]


def scrape_a7_completo(max_paginas=100):
    todos_imoveis = []
    pagina = 1
    
    while pagina <= max_paginas:
        if pagina == 1:
            url = "https://a7imobiliaria.com/imoveis"
        else:
            url = f"https://a7imobiliaria.com/imoveis.php?pagination={pagina}"
        
        print(f"Raspando página {pagina}: {url}")
        itens = scrape_pagina(url)
        
        if not itens:
            print(f"Página {pagina} veio vazia — parando.")
            break
        
        print(f"  → {len(itens)} imóveis encontrados")
        todos_imoveis.extend(itens)
        pagina += 1
        time.sleep(2)
    
    return todos_imoveis


def salvar_json(dados, caminho):
    """Salva os dados brutos em JSON, criando a pasta se não existir"""
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {len(dados)} imóveis em {caminho}")


# Coleta
imoveis_a7 = scrape_a7_completo()
print(f"\nTotal coletado: {len(imoveis_a7)}")

# Validação
print(f"Sem preço: {sum(1 for i in imoveis_a7 if not i['preco'])}")
print(f"Sem bairro: {sum(1 for i in imoveis_a7 if not i['bairro'])}")

links = [i['link'] for i in imoveis_a7]
print(f"Links únicos: {len(set(links))} de {len(links)}")

print(f"Bairros únicos: {set(i['bairro'] for i in imoveis_a7 if i['bairro'])}")

# Salvamento
salvar_json(imoveis_a7, "data/raw/a7_bruto.json")