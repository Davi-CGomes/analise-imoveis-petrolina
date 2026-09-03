# Análise de preços de imóveis em Petrolina/PE

Coleta e análise de anúncios de venda de imóveis em Petrolina, Pernambuco, a partir de duas fontes públicas: a OLX e o site da A7 Imobiliária. O objetivo é comparar preço mediano e preço por metro quadrado entre bairros da cidade.

Todo o dado foi coletado por scraping próprio, não há dataset pronto neste projeto.

**Amostra final:** 1.357 anúncios de venda, distribuídos em 63 bairros, dos quais 17 têm 20 ou mais anúncios e permitem análise comparativa. 86% dos anúncios informam a metragem, viabilizando o cálculo de preço por metro quadrado.

---

## Por que Petrolina

Análises de mercado imobiliário costumam usar dados de São Paulo ou Rio de Janeiro, já disponíveis em datasets públicos. Cidades médias do interior não têm esse dado organizado, o que torna a coleta parte do trabalho, e não uma etapa pulada.

Isso trouxe limitações reais, documentadas mais abaixo em vez de escondidas.

---

## Estrutura

```
petrolina-imoveis/
├── scrapers/
│   ├── a7.py                          Coleta A7 Imobiliária
│   └── olx.py                         Coleta da OLX
├── limpeza.py                         Conversão/padronização
├── consolidar.py                      Junta fontes e gera CSV
├── analise_bairros.py                 Exploração inicial 
├── notebooks/
│   └── analise_exploratoria.ipynb     Análise e gráficos
├── data/
│   ├── raw/                           JSON bruto
│   └── processed/                     CSV consolidado
└── requirements.txt
```

---

## Como rodar

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

python scrapers/a7.py             # gera data/raw/a7_bruto.json
python scrapers/olx.py            # gera data/raw/olx_venda_bruto.json
python consolidar.py              # gera data/processed/imoveis_consolidado.csv
```

A análise e os gráficos ficam em `notebooks/analise_exploratoria.ipynb`.

Os scrapers têm pausa de 2 a 3 segundos entre requisições. A coleta completa leva alguns minutos.

---

## O que foi encontrado

### A oferta anunciada é fortemente concentrada

Os cinco bairros com mais anúncios, Centro, Loteamento Recife, Boa Esperança, Cohab São Francisco e Dom Avelar, concentram cerca de 44% de toda a amostra. Os 17 bairros analisáveis somam 78%. A cauda de 34 bairros com menos de 10 anúncios representa pouco mais de 10% do total.

Isso reflete como a oferta se distribui na cidade, mas significa que conclusões sobre bairros pequenos são frágeis.

### Preço absoluto e preço por m² andam quase juntos

A hipótese inicial era encontrar bairros caros no valor total mas baratos por metro quadrado, indicando imóveis grandes, e vice-versa. O resultado foi uma correlação positiva bastante limpa: bairro caro no total tende a ser caro por metro.

As exceções são o achado real desta pergunta:

| Bairro | Preço mediano | Preço/m² mediano | Leitura |
|---|---|---|---|
| Atrás da Banca | R$ 700 mil | R$ 7.634 | Imóveis pequenos e valorizados: 3º maior preço/m² com preço absoluto médio |
| Vila Mocó | R$ 400 mil | R$ 5.456 | Mesmo padrão em escala menor, supera bairros bem mais caros no valor total |
| Vila Eulália | R$ 430 mil | R$ 2.560 | O oposto: menor preço/m² do conjunto, imóveis grandes e baratos por metro |

### A dispersão de preço varia muito entre bairros

Medida pelo IQR relativo (intervalo interquartil dividido pela mediana), que permite comparar bairros de faixas de preço diferentes:

- **Maior dispersão:** Fernando Idalino (1,28), primeiro quartil em R$ 318 mil e terceiro em R$ 2,05 milhões no mesmo bairro
- **Menor dispersão:** Antônio Cassimiro (0,62), seguido de Cidade Universitária e Dom Avelar (0,57)

Dispersão alta indica mercado heterogêneo, com mais margem de negociação e menos previsibilidade. Parte dela, porém, é artefato de classificação ver limitações.

### Diferença entre fontes: um achado que não sobreviveu ao controle

Comparando o preço mediano da A7 com o da OLX nos bairros onde ambas têm ao menos cinco anúncios, a A7 apareceu sistematicamente mais barata entre 17% e 52%.

Ao verificar a área mediana dos imóveis de cada fonte no mesmo bairro, ficou claro que as fontes anunciam imóveis de tamanhos muito diferentes. Em São José, a A7 tinha mediana de 1.220 m² contra 147 m² da OLX. Em Antônio Cassimiro, 57 m² contra 80 m².

Repetindo a comparação com **preço por m²** em vez de preço absoluto, o sinal inverteu em um dos casos: Antônio Cassimiro passou de "A7 17,6% mais barata" para "A7 36,1% mais cara".

**O que resta afirmar:** em 2 dos 4 bairros com composição comparável, a A7 apresentou preço por metro quadrado entre 26% e 30% inferior ao da OLX. Com 7 a 23 anúncios da A7 por bairro, isso é indício, não evidência suficiente para generalizar. Um dos dois bairros é Boa Esperança, cuja composição é afetada pela presença de condomínios de alto padrão a diferença ali pode refletir quanto de cada portfólio é composto por esses empreendimentos, não política de precificação.

---

## Decisões técnicas

**Nenhuma das fontes exigiu navegador automatizado.** Ambas entregam HTML renderizado no servidor, então `requests` e `BeautifulSoup` bastaram.

**A paginação da OLX não termina.** Ao esgotar os anúncios de Petrolina, a plataforma continua servindo resultados de outras cidades, incluindo São Paulo. Um scraper que para apenas quando a página vem vazia entra em loop indefinido. A solução foi filtrar por cidade dentro do próprio código, a cada página, e parar quando nenhum anúncio local aparece, sem depender do filtro do site.

**Dado bruto é salvo antes de qualquer tratamento.** Os JSONs em `data/raw/` preservam a resposta original das fontes, permitindo reprocessar a limpeza sem repetir a coleta, que é a etapa lenta e sujeita a falha.

**Deduplicação é feita pelo link do anúncio, não pelo título.** Títulos se repetem entre imóveis distintos, unidades iguais no mesmo condomínio, por exemplo.

**Bairros são normalizados antes de agrupar.** Sem isso, "Boa esperança" e "Boa Esperança" viram dois registros separados, dividindo a amostra e distorcendo a mediana de cada metade.

**Anúncios abaixo de R$ 50 mil são descartados.** Corte metodológico, não derivado dos dados: elimina aluguéis que aparecem na busca de venda e anúncios em que o valor da entrada foi cadastrado como preço do imóvel ("ENTRADA A PARTIR DE 15.000,00"). Foram 24 casos.

**A mediana é usada no lugar da média.** Com imóveis de até R$ 6,2 milhões na amostra, a média não representa o mercado de nenhum bairro.

---

## Limitações

Estas ressalvas são parte do resultado, não notas de rodapé.

**Preço de anúncio não é preço de venda.** Todos os valores são o que o anunciante pede, sistematicamente acima do que é fechado na prática. Corrigir isso exigiria dados de cartório, indisponíveis publicamente.

**Condomínios fechados distorcem o ranking dos bairros mais caros.** Anunciantes cadastram o bairro mais próximo quando o empreendimento fica fora dele. Isso afeta diretamente os dois primeiros colocados: **Boa Esperança** aparece como bairro mais caro da cidade por conta da concentração de anúncios do Alphaville, e **Fernando Idalino** aparece em segundo por motivo equivalente, resultado que não corresponde ao perfil real do bairro. O ranking de preço por bairro não deve ser lido sem essa ressalva.

**Terrenos, imóveis rurais e comerciais estão misturados aos residenciais.** A análise não segmenta por tipo de imóvel, então a mediana de um bairro pode combinar terreno de mil metros quadrados, loja comercial e apartamento de 57 m² no mesmo cálculo. Bairros com presença rural ou de terrenos grandes têm preço por metro quadrado artificialmente baixo em relação ao mercado residencial.

**A amostra é um retrato instantâneo.** A coleta foi feita de uma vez, não ao longo de semanas. Não captura variação de preço nem tempo de permanência do anúncio.

**As duas fontes têm pesos muito diferentes.** A OLX responde por 1.249 anúncios e a A7 por 108.

## Stack

Python, `requests`, `BeautifulSoup`, `pandas`, `matplotlib`.
