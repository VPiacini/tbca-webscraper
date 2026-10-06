import os

import psycopg2

ARQUIVO_TXT = 'queries.txt'

QUERIES = [
    "INSERT INTO Produto (Produto_id, nome, categoria) VALUES (%s, %s, %s);",
    "INSERT INTO Macronutrientes (Produto_id, calorias, carboidratos, acucares_totais, acucares_adicionados, proteinas, gorduras_saturadas, gorduras_trans, fibra) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
    "INSERT INTO Minerais (Produto_id, calcio, ferro, magnesio, fosforo, potassio, sodio, zinco, cobre, manganes, selenio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
    "INSERT INTO Vitaminas (Produto_id, vitaminaA, vitaminaE, vitaminaD, vitaminaC, vitaminaK, tiamina, riboflavina, niacina, vitaminaB6, folato, vitaminaB12) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
]


def conectar():
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'Tabela_Completa'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ['DB_PASS'],
        host=os.environ.get('DB_HOST', 'localhost'),
    )


def saveInSQLandTxt(conn, Produto, Macronutrientes, Minerais, Vitaminas):
    with conn.cursor() as cursor, open(ARQUIVO_TXT, 'a', encoding='UTF-8') as f:
        for query, valores in zip(QUERIES, [Produto, Macronutrientes, Minerais, Vitaminas]):
            sql = cursor.mogrify(query, valores)
            cursor.execute(sql)
            f.write('\n' + sql.decode('UTF-8'))
        f.write('\n')
    conn.commit()
