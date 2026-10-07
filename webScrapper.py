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

# Coluna no banco -> componente na TBCA. Valores por 100 g, na unidade original da TBCA (ver schema.sql).
# Componentes que a TBCA não informa ficam NULL.
TABELAS = {
    'Macronutrientes': {
        'calorias': 'Energia',  # kcal (a linha em kJ é ignorada)
        'carboidratos': 'Carboidrato total',
        'acucares_totais': 'Açúcar total',  # não existe na TBCA
        'acucares_adicionados': 'Açúcar de adição',
        'proteinas': 'Proteína',
        'gorduras_totais': 'Lipídios',
        'gorduras_saturadas': 'Ácidos graxos saturados',
        'gorduras_monoinsaturadas': 'Ácidos graxos monoinsaturados',
        'gorduras_poliinsaturadas': 'Ácidos graxos poliinsaturados',
        'gorduras_trans': 'Ácidos graxos trans',
        'colesterol': 'Colesterol',
        'fibra': 'Fibra alimentar',
    },
    'Minerais': {
        'calcio': 'Cálcio', 'ferro': 'Ferro', 'magnesio': 'Magnésio', 'fosforo': 'Fósforo', 'potassio': 'Potássio',
        'sodio': 'Sódio', 'zinco': 'Zinco', 'cobre': 'Cobre', 'manganes': 'Manganês', 'selenio': 'Selênio',
    },
    'Vitaminas': {
        'vitaminaA': 'Vitamina A (RAE)',
        'vitaminaE': 'Alfa-tocoferol (Vitamina E)',
        'vitaminaD': 'Vitamina D',
        'vitaminaC': 'Vitamina C',
        'vitaminaK': 'Vitamina K',  # não existe na TBCA
        'tiamina': 'Tiamina',
        'riboflavina': 'Riboflavina',
        'niacina': 'Niacina',
        'vitaminaB6': 'Vitamina B6',
        'folato': 'Equivalente de folato',
        'vitaminaB12': 'Vitamina B12',
    },
}


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


def lerValor(valor):
    if valor == 'tr':  # traço: presente em quantidade não quantificável
        return 0
    if valor in ('NA', '-', ''):  # não analisado: desconhecido, não zero
        return None
    return float(valor.replace(',', '.'))


def lerProduto(id, soup):
    """Devolve {tabela: {coluna: valor}} na ordem de inserção."""
    cabecalho = soup.find('h5').get_text(' ', strip=True)
    letra, grupo = re.search(r'Grupo: (\w) - (.+?) Tipo', cabecalho).groups()
    nome = re.search(r'Descrição: (.+?)(?: <<|$)', cabecalho).group(1)

    valores = {}
    for row in soup.find('table').find_all('tr'):
        celulas = [cell.get_text(strip=True) for cell in row.find_all('td')]
        if celulas and celulas[2] != 'kJ':  # componente, tagname, unidade, valor por 100 g, ...
            valores[celulas[0]] = lerValor(celulas[3])

    linhas = {'Produto': {'Produto_id': id, 'nome': nome, 'categoria': CATEGORIAS.get(letra, grupo)}}
    for tabela, colunas in TABELAS.items():
        linhas[tabela] = {'Produto_id': id} | {coluna: valores.get(c) for coluna, c in colunas.items()}
    return linhas


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
                addToSQL.saveInSQLandTxt(conn, lerProduto(id, baixar(link)))
                novos += 1
                log.info('%s salvo', codigo)
            except Exception:
                conn.rollback()
                erros += 1
                log.exception('Falha ao processar %s', codigo)
    log.info('Fim: %d novos, %d erros', novos, erros)


if __name__ == '__main__':
    main()
