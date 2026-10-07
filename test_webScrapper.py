from bs4 import BeautifulSoup as bs

import webScrapper as w

# HTML sintético no mesmo formato da página de um alimento da TBCA
PAGINA = '''
<h5><strong>Código:</strong> BRC9999A <strong>Grupo:</strong> A - Cereais e derivados
<strong>Tipo de Alimento:</strong> B - Ingrediente <strong>Descrição:</strong> Alimento teste, cru << Test food</h5>
<table><tr><th>Componente</th></tr>
<tr><td>Energia</td><td>ENERC</td><td>kJ</td><td>418</td></tr>
<tr><td>Energia</td><td>ENERC</td><td>kcal</td><td>100</td></tr>
<tr><td>Lipídios</td><td>FAT</td><td>g</td><td>2,5</td></tr>
<tr><td>Cálcio</td><td>CA</td><td>mg</td><td>tr</td></tr>
<tr><td>Ferro</td><td>FE</td><td>mg</td><td>NA</td></tr>
<tr><td>Selênio</td><td>SE</td><td>mcg</td><td>1,9</td></tr>
<tr><td>Vitamina A (RE)</td><td>VITA</td><td>mcg</td><td>10</td></tr>
<tr><td>Vitamina A (RAE)</td><td>VITA RAE</td><td>mcg</td><td>5</td></tr>
<tr><td>Açúcar de adição</td><td>—</td><td>g</td><td>3</td></tr>
</table>'''


def test_lerProduto():
    linhas = w.lerProduto('9999A', bs(PAGINA, 'html.parser'))
    assert list(linhas) == ['Produto', 'Macronutrientes', 'Minerais', 'Vitaminas']  # Produto primeiro, por causa das FKs
    assert linhas['Produto'] == {'Produto_id': '9999A', 'nome': 'Alimento teste, cru', 'categoria': 'Cereais e derivados'}

    macro, minerais, vitaminas = linhas['Macronutrientes'], linhas['Minerais'], linhas['Vitaminas']
    assert macro['calorias'] == 100  # kcal, não kJ
    assert macro['gorduras_totais'] == 2.5
    assert macro['acucares_adicionados'] == 3
    assert macro['acucares_totais'] is None  # não existe na TBCA
    assert minerais['calcio'] == 0  # 'tr' vira 0
    assert minerais['ferro'] is None  # 'NA' vira NULL
    assert minerais['selenio'] == 1.9  # unidade original (µg)
    assert vitaminas['vitaminaA'] == 5  # RAE, não RE
    assert vitaminas['vitaminaK'] is None


if __name__ == '__main__':
    test_lerProduto()
    print('ok')
