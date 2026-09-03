import re
import unicodedata


def limpar_preco(preco_str):
    # Converte 'R$ 350.000' em 350000.0, tratando o formato numérico brasileiro.
    if not preco_str:
        return None
    numeros = re.sub(r'[^\d,\.]', '', preco_str)
    if not numeros:
        return None
    # No padrão BR o ponto separa milhar e a vírgula é decimal — invertido em relação ao float
    numeros = numeros.replace('.', '').replace(',', '.')
    try:
        return float(numeros)
    except ValueError:
        return None


def limpar_area(area_str):
    # Converte '200m²' em 200.0. Área zerada vira None (não informada, não zero).
    if not area_str:
        return None
    numeros = re.sub(r'[^\d,\.]', '', area_str)
    if not numeros:
        return None
    numeros = numeros.replace(',', '.')
    try:
        valor = float(numeros)
        # A A7 preenche "0.00 m²" quando o anunciante não informa a metragem
        return valor if valor > 0 else None
    except ValueError:
        return None


def limpar_int(valor_str):
    # Converte texto de quartos, banheiros ou vagas em inteiro.
    if not valor_str:
        return None
    numeros = re.sub(r'[^\d]', '', str(valor_str))
    return int(numeros) if numeros else None


def normalizar_finalidade(valor):
    # Unifica 'Para Venda' (A7) e 'venda' (OLX) num único vocabulário.
    if not valor:
        return None
    v = valor.lower()
    if 'venda' in v:
        return 'venda'
    if 'alug' in v or 'locac' in v:
        return 'aluguel'
    return v


def normalizar_bairro(texto):
    # Padroniza acentuação, caixa e espaços para que o mesmo bairro não vire dois registros.
    if not texto:
        return None
    t = texto.strip().lower()
    t = unicodedata.normalize('NFKD', t).encode('ASCII', 'ignore').decode('utf-8')
    return ' '.join(t.split()).title()