import sqlite3

DATABASE_PATH = './scripts/DB/my_database.db'

def create_table():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_time TEXT NOT NULL
    );
    """
    cursor.execute(create_table_query)
    connection.commit()
    connection.close()

def insert_current_datetime():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    
    current_datetime = "asdasd"
    insert_query = "INSERT INTO test (date_time) VALUES (?);"
    cursor.execute(insert_query, (current_datetime,))
    
    connection.commit()
    connection.close()


def run_test():
    create_table()
    insert_current_datetime()
run_test()