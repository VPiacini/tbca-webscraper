import sys

import requests
from bs4 import BeautifulSoup as bs

import addToSQL

URL = 'https://www.tbca.net.br/base-dados/int_composicao_alimentos.php?cod_produto='

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
ALFABETO = list(CATEGORIAS)

# Fatores para converter cada unidade em gramas (energia fica como está)
PARA_GRAMAS = {'g': 1, 'mg': 1 / 1000, 'mcg': 1 / 1_000_000, 'kJ': 1, 'kcal': 1}


def nextID(lastID):
    """BRC0001A -> BRC0001B ... BRC0001U -> BRC0002A"""
    prefixo, numero, letra = lastID[:3], int(lastID[3:7]), lastID[7]
    if letra == ALFABETO[-1]:
        return f'{prefixo}{numero + 1:04d}{ALFABETO[0]}'
    return f'{prefixo}{numero:04d}{ALFABETO[ALFABETO.index(letra) + 1]}'


def paraGramas(unidade, valor):
    if valor in ('tr', 'NA', '-', ''):
        return 0
    if unidade not in PARA_GRAMAS:
        raise ValueError('Novo tipo de unidade não mensurado para gramas: ' + unidade)
    return float(valor.replace(',', '.')) * PARA_GRAMAS[unidade]


def scrapperToSQL(conn, url, id):
    """Retorna True se o produto existia e foi salvo."""
    soup = bs(requests.get(url, timeout=30).text, features='html.parser')
    table = soup.find('table')
    if table is None or table.find('td') is None:
        return False

    nome = soup.find('h5').find_all('strong')[1].next_sibling
    fim = nome.index('<') - 3 if '<' in nome else len(nome) - 2
    nomeLimpo = nome[1:fim]

    dados = []
    for row in table.find_all('tr'):
        celulas = [cell.text for cell in row.find_all('td')]
        if celulas:
            dados.append(paraGramas(celulas[1], celulas[2]))

    Produto = [id, nomeLimpo, CATEGORIAS[id[4]]]
    # calorias, carboidratos, acucares_totais, acucares_adicionados, proteinas, gorduras_saturadas, gorduras_trans, fibra
    Macronutrientes = [id, dados[0], dados[3], dados[37], dados[37], dados[5], dados[11], dados[14], dados[7]]
    # calcio, ferro, magnesio, fosforo, potassio, sodio, zinco, cobre, manganes, selenio
    Minerais = [id, dados[15], dados[16], dados[18], dados[19], dados[20], dados[17], dados[22], dados[23], dados[21], dados[24]]
    # vitaminaA, vitaminaE, vitaminaD, vitaminaC, vitaminaK (não existe na TBCA), tiamina, riboflavina, niacina, vitaminaB6, folato, vitaminaB12
    Vitaminas = [id, dados[25], dados[28], dados[27], dados[34], None, dados[29], dados[30], dados[31], dados[32], dados[35], dados[33]]

    addToSQL.saveInSQLandTxt(conn, Produto, Macronutrientes, Minerais, Vitaminas)
    return True


if __name__ == '__main__':
    # Uso: python webScrapper.py [ID_INICIAL] [QUANTIDADE]
    lastID = sys.argv[1] if len(sys.argv) > 1 else 'BRC0001A'
    quantidade = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    vazios = 0

    with addToSQL.conectar() as conn:
        for i in range(quantidade):
            print(lastID[3:8], i, vazios, i - vazios)
            if not scrapperToSQL(conn, URL + lastID, lastID[3:8]):
                vazios += 1
            lastID = nextID(lastID)
