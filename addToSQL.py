import os

import psycopg2

ARQUIVO_TXT = 'queries.txt'


def conectar():
    return psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'Tabela_Completa'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ['DB_PASS'],
        host=os.environ.get('DB_HOST', 'localhost'),
    )


def idsSalvos(conn):
    with conn.cursor() as cursor:
        cursor.execute('SELECT Produto_id FROM Produto;')
        return {linha[0] for linha in cursor}


def saveInSQLandTxt(conn, linhas):
    """linhas: {tabela: {coluna: valor}}. Nomes de tabela e coluna vêm do código, nunca do site."""
    with conn.cursor() as cursor:
        sqls = []
        for tabela, linha in linhas.items():
            query = f"INSERT INTO {tabela} ({', '.join(linha)}) VALUES ({', '.join(['%s'] * len(linha))});"
            sqls.append(cursor.mogrify(query, list(linha.values())).decode('UTF-8'))
        for sql in sqls:
            cursor.execute(sql)
    conn.commit()
    # Só grava no txt depois do commit, para o arquivo não ter produtos pela metade
    with open(ARQUIVO_TXT, 'a', encoding='UTF-8') as f:
        f.write('\n' + '\n'.join(sqls) + '\n')
