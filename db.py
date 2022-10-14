import sqlite3

__connection = None


def get_connection():
    global __connection
    if __connection is None:
        __connection = sqlite3.connect(
            'database.db',
            check_same_thread = False
        )

    return __connection


conn = get_connection()
c = conn.cursor()


c.execute('''CREATE TABLE IF NOT EXISTS reminds(
        id     INTEGER PRIMARY KEY AUTOINCREMENT,
        date    VARCHAR(255),
        title    VARCHAR(255),
        text    VARCHAR(255)
    )
''')
conn.commit()


def select_data():
    return c.execute("SELECT date, title, text FROM reminds").fetchall()

def check_data(title):
    return c.execute("SELECT text FROM reminds WHERE title = ?", (title,)).fetchone()

def insert_data(date, title, text):
    c.execute("INSERT INTO reminds (date, title, text) VALUES (?, ?, ?)", (date, title, text,))
    conn.commit()

def row_count():
    return c.execute('SELECT COUNT(*) FROM reminds').fetchone()[0]

def delete_data(data):
    c.execute("DELETE FROM reminds WHERE title = ? OR text = ?", (data, data))
    conn.commit()