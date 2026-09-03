import requests
from bs4 import BeautifulSoup
import time
import json


def parse_card_olx(section):
    """Extrai os dados de um card de anúncio da OLX"""
    
    # Título e link
    link_tag = section.select_one('a.olx-adcard__link')
    titulo = link_tag.get('title') if link_tag else None
    link = link_tag.get('href') if link_tag else None
    
    # Preço
    preco_tag = section.select_one('h3.olx-adcard__price')
    preco = preco_tag.get_text(strip=True) if preco_tag else None
    
    # Localização (formato esperado: "Cidade, Bairro")
    localizacao_tag = section.select_one('p.olx-adcard__location')
    localizacao = localizacao_tag.get_text(strip=True) if localizacao_tag else None
    bairro = None
    if localizacao and ',' in localizacao:
        bairro = localizacao.split(',', 1)[1].strip()
    
    # Data do anúncio
    data_tag = section.select_one('p.olx-adcard__date')
    data_anuncio = data_tag.get_text(strip=True) if data_tag else None
    
    # Detalhes via aria-label (mais confiável que posição)
    area = quartos = banheiros = vagas = None
    for detail in section.select('div.olx-adcard__detail'):
        aria = detail.get('aria-label', '')
        valor = detail.get_text(strip=True)
        
        if 'metro' in aria:
            area = valor
        elif 'quarto' in aria:
            quartos = valor
        elif 'banheiro' in aria:
            banheiros = valor
        elif 'vaga' in aria:
            vagas = valor
    
    # Badge do anunciante (ex: "Direto com o proprietário")
    badge_tag = section.select_one('.olx-core-badge')
    tipo_anunciante = badge_tag.get_text(strip=True) if badge_tag else None
    
    return {
        'titulo': titulo,
        'preco': preco,
        'localizacao_completa': localizacao,
        'bairro': bairro,
        'area': area,
        'quartos': quartos,
        'banheiros': banheiros,
        'vagas': vagas,
        'data_anuncio': data_anuncio,
        'tipo_anunciante': tipo_anunciante,
        'link': link,
        'fonte': 'OLX'
    }


def scrape_pagina_olx(url, finalidade):
    """Raspa uma única página de resultados da OLX"""
    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    soup = BeautifulSoup(r.text, 'html.parser')
    cards = soup.select('section.olx-adcard')
    
    resultados = [parse_card_olx(c) for c in cards]
    for item in resultados:
        item['finalidade'] = finalidade
    
    return resultados


def scrape_olx_completo(url_base, finalidade, max_paginas=100, cidade_alvo="Petrolina"):
    todos_imoveis = []
    pagina = 1
    
    while pagina <= max_paginas:
        url = url_base if pagina == 1 else f"{url_base}?o={pagina}"
        
        print(f"Raspando página {pagina}: {url}")
        itens = scrape_pagina_olx(url, finalidade)
        
        if not itens:
            print(f"Página {pagina} veio vazia — parando.")
            break
        
        # Mantém só os que são da cidade alvo
        itens_validos = [
            i for i in itens
            if i['localizacao_completa'] and cidade_alvo.lower() in i['localizacao_completa'].lower()
        ]
        
        print(f"  → {len(itens_validos)} de {cidade_alvo} ({len(itens)} no total da página)")
        
        # Se a página inteira veio de fora, esgotou os resultados locais
        if not itens_validos:
            print(f"Página {pagina} não tem imóveis de {cidade_alvo} — parando.")
            break
        
        todos_imoveis.extend(itens_validos)
        pagina += 1
        time.sleep(3)
    
    return todos_imoveis

def salvar_json(dados, caminho):
    """Salva os dados brutos em JSON"""
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"Salvo: {len(dados)} imóveis em {caminho}")

URL_VENDA = "https://www.olx.com.br/imoveis/venda/estado-pe/regiao-de-petrolina-e-garanhuns/petrolina"

# Teste completo
imoveis_olx = scrape_olx_completo(URL_VENDA, finalidade="venda")
print(f"\nTotal no teste: {len(imoveis_olx)}")

# Salvar em JSON
salvar_json(imoveis_olx, "data/raw/olx_venda_bruto.json")

