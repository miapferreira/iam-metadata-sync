import mysql.connector
from config import DB_CONFIG

# Conecta sem passar o nome do banco
conn = mysql.connector.connect(
    host=DB_CONFIG['host'],
    user=DB_CONFIG['user'],
    password=DB_CONFIG['password'],
    port=DB_CONFIG['port']
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS iam_metadata")
print("✅ Banco de dados 'iam_metadata' criado com sucesso.")

cursor.close()
conn.close()
