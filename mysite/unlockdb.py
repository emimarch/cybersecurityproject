from sqlite3 import dbapi2 as sqlite


def unlock_db():
    """Replace db_filename with the name of the SQLite database."""
    connection = sqlite.connect('db.sqlite3')
    connection.commit()
    connection.close()




def main():
    unlock_db()