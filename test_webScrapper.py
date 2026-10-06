import math

from bs4 import BeautifulSoup as bs

import webScrapper as w

# HTML sintético no mesmo formato da página de um alimento da TBCA
PAGINA = '''
<h5><strong>Código:</strong> BRC9999A <strong>Grupo:</strong> A - Cereais e derivados
<strong>Tipo de Alimento:</strong> B - Ingrediente <strong>Descrição:</strong> Alimento teste, cru << Test food</h5>
<table><tr><th>Componente</th></tr>
<tr><td>Energia</td><td>ENERC</td><td>kJ</td><td>418</td></tr>
<tr><td>Energia</td><td>ENERC</td><td>kcal</td><td>100</td></tr>
<tr><td>Proteína</td><td>PROCNT</td><td>g</td><td>2,5</td></tr>
<tr><td>Cálcio</td><td>CA</td><td>mg</td><td>tr</td></tr>
<tr><td>Selênio</td><td>SE</td><td>mcg</td><td>1,9</td></tr>
</table>'''


def test_lerProduto():
    Produto, Macro, Minerais, Vitaminas = w.lerProduto('9999A', bs(PAGINA, 'html.parser'))
    assert Produto == ['9999A', 'Alimento teste, cru', 'Cereais e derivados']
    assert Macro[1] == 100  # kcal, não kJ
    assert Macro[5] == 2.5
    assert Minerais[1] == 0  # 'tr' vira 0
    assert math.isclose(Minerais[10], 1.9e-6)  # mcg -> g
    assert Vitaminas[5] is None  # vitamina K não existe na TBCA


if __name__ == '__main__':
    test_lerProduto()
    print('ok')
