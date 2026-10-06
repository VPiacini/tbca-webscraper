# TBCA Web Scraper

Web scraper para a [Tabela Brasileira de Composição de Alimentos (TBCA)](https://www.tbca.net.br/). Ele percorre as páginas de cada alimento da base, extrai os dados de composição e salva tudo em um banco PostgreSQL. Foi feito como parte de um TCC.

## Como funciona

Os códigos dos alimentos seguem o formato `BRC` + número de 4 dígitos + letra da categoria (ex.: `BRC0001A`). O script incrementa esse código, baixa cada página com `requests`, faz o parse da tabela com `BeautifulSoup`, converte todas as unidades para gramas e insere os dados com `psycopg2`.

Cada `INSERT` também é gravado em `queries.txt`, para recriar a base sem precisar raspar o site de novo.

### Tabelas

| Tabela | Colunas |
|---|---|
| `Produto` | Produto_id, nome, categoria |
| `Macronutrientes` | Produto_id, calorias, carboidratos, acucares_totais, acucares_adicionados, proteinas, gorduras_saturadas, gorduras_trans, fibra |
| `Minerais` | Produto_id, calcio, ferro, magnesio, fosforo, potassio, sodio, zinco, cobre, manganes, selenio |
| `Vitaminas` | Produto_id, vitaminaA, vitaminaE, vitaminaD, vitaminaC, vitaminaK, tiamina, riboflavina, niacina, vitaminaB6, folato, vitaminaB12 |

Existe ainda uma tabela fixa, `Categoria`, com as categorias possíveis. As tabelas precisam existir antes da execução.

## Uso

```bash
pip install -r requirements.txt
```

A conexão é configurada por variáveis de ambiente: `DB_PASS` (obrigatória), `DB_NAME` (padrão `Tabela_Completa`), `DB_USER` (padrão `postgres`) e `DB_HOST` (padrão `localhost`).

```bash
DB_PASS=sua_senha python webScrapper.py [ID_INICIAL] [QUANTIDADE]
```

Por padrão, o script começa em `BRC0001A` e testa 10.000 códigos. Passe outro ID para retomar de onde parou.

## Dados

O arquivo `queries.txt` contém os inserts de 4.919 alimentos, raspados em abril de 2024 com a versão anterior do script. Essa versão tinha dois erros que já foram corrigidos no código, mas continuam no arquivo:

- valores em `mcg` (por exemplo, selênio, folato e vitaminas A, D e B12) não foram convertidos para gramas;
- a coluna `vitaminaK` recebeu o valor de energia. A TBCA não informa vitamina K, então agora essa coluna fica `NULL`.

A coluna `calorias` usa a primeira linha da tabela da TBCA, que é a energia em kJ.
