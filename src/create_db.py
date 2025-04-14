import mysql.connector
from config import DB_CONFIG

def create_table():
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database']
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS iam_user_metadata (
            user_name VARCHAR(100) PRIMARY KEY,
            arn TEXT,
            create_date DATETIME,
            console_access VARCHAR(10),
            access_keys JSON,
            signing_certs JSON,
            tags JSON
        );
    """)

    print("Table 'iam_user_metadata' created successfully.")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_table()
