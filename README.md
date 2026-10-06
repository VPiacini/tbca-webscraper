# TBCA Web Scraper

Web scraper para a [Tabela Brasileira de Composição de Alimentos (TBCA)](https://www.tbca.net.br/). Ele percorre a listagem de alimentos da base, extrai os dados de composição de cada um e salva tudo em um banco PostgreSQL. Foi feito como parte de um TCC.

## Como funciona

1. Percorre as páginas da listagem em `composicao_estatistica.php` (100 alimentos por página) até encontrar uma página vazia.
2. Abre a página de cada alimento, lê o cabeçalho (código, grupo, descrição) e a tabela de componentes.
3. Converte todas as unidades para gramas (`mg` e `mcg`). A energia fica em kcal.
4. Insere o alimento nas quatro tabelas com `psycopg2`, em uma transação, e grava os mesmos `INSERT`s em `queries.txt`.

### Robustez

- Há uma pausa entre as requisições (padrão de 2 s, configurável em `PAUSA`). O site derruba a conexão quando recebe requisições em sequência rápida.
- Erros de conexão e respostas 429/5xx são tentados de novo até 5 vezes, com espera crescente.
- Uma falha em um alimento é registrada no log e a transação é desfeita, sem interromper o restante.
- Os alimentos que já estão no banco são pulados, então basta rodar de novo para retomar uma execução interrompida.
- O log é exibido no terminal e gravado em `scraper.log`.

### Tabelas

| Tabela | Colunas |
|---|---|
| `Produto` | Produto_id, nome, categoria |
| `Macronutrientes` | Produto_id, calorias (kcal), carboidratos, acucares_totais, acucares_adicionados, proteinas, gorduras_saturadas, gorduras_trans, fibra |
| `Minerais` | Produto_id, calcio, ferro, magnesio, fosforo, potassio, sodio, zinco, cobre, manganes, selenio |
| `Vitaminas` | Produto_id, vitaminaA, vitaminaE, vitaminaD, vitaminaC, vitaminaK, tiamina, riboflavina, niacina, vitaminaB6, folato, vitaminaB12 |

Existe ainda uma tabela fixa, `Categoria`, com as categorias possíveis. As tabelas precisam existir antes da execução.

O `Produto_id` é o código da TBCA sem o prefixo `BRC` (ex.: `0001A`). Os nutrientes estão em gramas por 100 g de alimento. A TBCA não informa açúcares totais nem vitamina K. Por isso, `acucares_totais` repete o açúcar de adição e `vitaminaK` fica `NULL`.

## Uso

```bash
pip install -r requirements.txt
```

A conexão é configurada por variáveis de ambiente: `DB_PASS` (obrigatória), `DB_NAME` (padrão `Tabela_Completa`), `DB_USER` (padrão `postgres`) e `DB_HOST` (padrão `localhost`).

```bash
DB_PASS=sua_senha python webScrapper.py
```

Para testar o parser sem acessar o site nem o banco:

```bash
python test_webScrapper.py
```

## Dados e termos de uso

Os dados extraídos não fazem parte deste repositório. Os [termos da TBCA](https://www.tbca.net.br/) estimulam a divulgação dos dados sem fins comerciais e com citação da fonte, mas proíbem a reprodução total ou parcial do material, a comercialização e a alteração do conteúdo. Por isso, `queries.txt` e o banco gerado são apenas para uso local. Para uso comercial, é preciso contatar os coordenadores da TBCA (tbca.contato@usp.br).

Fonte: Tabela Brasileira de Composição de Alimentos (TBCA). Universidade de São Paulo (USP). Centro de Pesquisa em Alimentos (FoRC). Versão 7.3. São Paulo, 2025. Disponível em http://www.fcf.usp.br/tbca.
