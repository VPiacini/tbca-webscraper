import logging
import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import addToSQL

BASE = 'https://www.tbca.net.br/base-dados/'
PAUSA = float(os.environ.get('PAUSA', 2))  # segundos entre requisições; o site derruba conexões em sequência rápida

log = logging.getLogger('tbca')

sessao = requests.Session()
sessao.mount('https://', HTTPAdapter(max_retries=Retry(total=5, backoff_factor=5, status_forcelist=[429, 500, 502, 503, 504])))

CATEGORIAS = {
    'A': 'Cereais e derivados',
    'B': 'Vegetais e derivados',
    'C': 'Frutas e derivados',
    'D': 'Gorduras e óleos',
    'E': 'Pescados e frutos do mar',
    'F': 'Carnes e derivados',
    'G': 'Leites e derivados',
    'H': 'Bebidas',
    'J': 'Ovos e derivados',
    'K': 'Açucares e doces',
    'L': 'Miscelâneas',
    'M': 'Fast Food',
    'N': 'Fins especiais',
    'R': 'Industrializados',
    'T': 'Leguminosas e derivados',
    'U': 'Nozes e sementes',
}

# Fatores para converter cada unidade em gramas (energia fica em kcal)
PARA_GRAMAS = {'g': 1, 'mg': 1 / 1000, 'mcg': 1 / 1_000_000, 'kcal': 1}

# Nome do componente na TBCA, na ordem das colunas de cada tabela
MACRONUTRIENTES = ['Energia', 'Carboidrato total', 'Açúcar de adição', 'Açúcar de adição', 'Proteína',
                   'Ácidos graxos saturados', 'Ácidos graxos trans', 'Fibra alimentar']
MINERAIS = ['Cálcio', 'Ferro', 'Magnésio', 'Fósforo', 'Potássio', 'Sódio', 'Zinco', 'Cobre', 'Manganês', 'Selênio']
VITAMINAS = ['Vitamina A (RE)', 'Alfa-tocoferol (Vitamina E)', 'Vitamina D', 'Vitamina C',
             'Vitamina K',  # não existe na TBCA, fica NULL
             'Tiamina', 'Riboflavina', 'Niacina', 'Vitamina B6', 'Equivalente de folato', 'Vitamina B12']


def baixar(caminho, **params):
    time.sleep(PAUSA)
    resposta = sessao.get(BASE + caminho, params=params, timeout=30)
    resposta.raise_for_status()
    return bs(resposta.text, features='html.parser')


def listarProdutos():
    """Percorre a listagem paginada e devolve (código, link) de cada alimento."""
    pagina = 1
    while True:
        links = baixar('composicao_estatistica.php', pagina=pagina).select('tbody tr td:first-child a')
        if not links:
            return
        log.info('Página %d: %d alimentos', pagina, len(links))
        for a in links:
            yield a.text.strip(), a['href']
        pagina += 1


def paraGramas(unidade, valor):
    if valor in ('tr', 'NA', '-', ''):
        return 0
    if unidade not in PARA_GRAMAS:
        raise ValueError('Novo tipo de unidade não mensurado para gramas: ' + unidade)
    return float(valor.replace(',', '.')) * PARA_GRAMAS[unidade]


def lerProduto(id, soup):
    cabecalho = soup.find('h5').get_text(' ', strip=True)
    letra, grupo = re.search(r'Grupo: (\w) - (.+?) Tipo', cabecalho).groups()
    nome = re.search(r'Descrição: (.+?)(?: <<|$)', cabecalho).group(1)

    valores = {}
    for row in soup.find('table').find_all('tr'):
        celulas = [cell.get_text(strip=True) for cell in row.find_all('td')]
        if celulas and celulas[2] != 'kJ':  # componente, tagname, unidade, valor por 100 g, ...
            valores[celulas[0]] = paraGramas(celulas[2], celulas[3])

    Produto = [id, nome, CATEGORIAS.get(letra, grupo)]
    Macronutrientes = [id] + [valores.get(c) for c in MACRONUTRIENTES]
    Minerais = [id] + [valores.get(c) for c in MINERAIS]
    Vitaminas = [id] + [valores.get(c) for c in VITAMINAS]
    return Produto, Macronutrientes, Minerais, Vitaminas


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler('scraper.log', encoding='UTF-8')])
    novos = erros = 0
    with addToSQL.conectar() as conn:
        salvos = addToSQL.idsSalvos(conn)  # permite retomar uma execução interrompida
        log.info('%d alimentos já estão no banco', len(salvos))
        for codigo, link in listarProdutos():
            id = codigo[3:]  # BRC0001A -> 0001A
            if id in salvos:
                continue
            try:
                addToSQL.saveInSQLandTxt(conn, *lerProduto(id, baixar(link)))
                novos += 1
                log.info('%s salvo', codigo)
            except Exception:
                conn.rollback()
                erros += 1
                log.exception('Falha ao processar %s', codigo)
    log.info('Fim: %d novos, %d erros', novos, erros)


if __name__ == '__main__':
    main()
