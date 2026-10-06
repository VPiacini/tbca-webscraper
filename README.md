# TBCA Web Scraper

Web scraper for the [Brazilian Food Composition Table (TBCA)](https://www.tbca.net.br/). It walks through the database's food list, extracts the composition data for each food, and saves it to a PostgreSQL database. It was built as part of an undergraduate thesis (TCC).

## How it works

1. Goes through the pages of the listing at `composicao_estatistica.php` (100 foods per page) until it reaches an empty page.
2. Opens each food's page and reads the header (code, group, description) and the component table.
3. Converts every unit to grams (`mg` and `mcg`). Energy stays in kcal.
4. Inserts the food into the four tables with `psycopg2` in a single transaction, and appends the same `INSERT` statements to `queries.txt`.

### Reliability

- The scraper pauses between requests (2 s by default, set with `PAUSA`). The site drops the connection when requests come in quick succession.
- Connection errors and 429/5xx responses are retried up to 5 times, with increasing waits.
- If one food fails, the error is logged and its transaction is rolled back. The rest of the run continues.
- Foods already in the database are skipped, so running the script again resumes an interrupted run.
- The log is printed to the terminal and written to `scraper.log`.

### Tables

| Table | Columns |
|---|---|
| `Produto` | Produto_id, nome, categoria |
| `Macronutrientes` | Produto_id, calorias (kcal), carboidratos, acucares_totais, acucares_adicionados, proteinas, gorduras_saturadas, gorduras_trans, fibra |
| `Minerais` | Produto_id, calcio, ferro, magnesio, fosforo, potassio, sodio, zinco, cobre, manganes, selenio |
| `Vitaminas` | Produto_id, vitaminaA, vitaminaE, vitaminaD, vitaminaC, vitaminaK, tiamina, riboflavina, niacina, vitaminaB6, folato, vitaminaB12 |

There is also a fixed `Categoria` table with the possible categories. The tables must exist before running the scraper.

`Produto_id` is the TBCA code without the `BRC` prefix (e.g. `0001A`). Nutrients are in grams per 100 g of food. TBCA does not report total sugars or vitamin K, so `acucares_totais` repeats the added sugar value and `vitaminaK` is `NULL`.

## Usage

```bash
pip install -r requirements.txt
```

The connection is set with environment variables: `DB_PASS` (required), `DB_NAME` (default `Tabela_Completa`), `DB_USER` (default `postgres`) and `DB_HOST` (default `localhost`).

```bash
DB_PASS=your_password python webScrapper.py
```

To test the parser without reaching the site or the database:

```bash
python test_webScrapper.py
```

## Data and terms of use

The scraped data is not part of this repository. [TBCA's terms](https://www.tbca.net.br/) encourage sharing the data for non-commercial purposes with the source cited, but they forbid reproducing the material in full or in part, selling it, or changing its content. For that reason, `queries.txt` and the generated database are for local use only. For commercial use, contact the TBCA coordinators (tbca.contato@usp.br).

Source: Tabela Brasileira de Composição de Alimentos (TBCA). Universidade de São Paulo (USP). Centro de Pesquisa em Alimentos (FoRC). Versão 7.3. São Paulo, 2025. Available at http://www.fcf.usp.br/tbca.
