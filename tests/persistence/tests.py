from config import database
from src.helpers.MariaDbDatabaseManager import MariaDbDatabaseManager
from src.persistence.DatabaseManagerStub import DatabaseManagerStub


def test1():
    new_song_name = 'OKOK'
    new_song_genre = 'Pop'
    db = DatabaseManagerStub()
    genre = db.get_song_genre(new_song_name)
    genre = db.get_song_genre('Melodie')
    song_id = db.insert_song_data_row(new_song_name)
    genre = db.get_song_genre(new_song_name)
    db.update_song_genre(song_id, new_song_genre)
    genre = db.get_song_genre(new_song_name)
    pass

def test2():
    db_man = MariaDbDatabaseManager(database.USER, database.PASSWORD,
                                    database.DATABASE, database.DB_HOST, database.DB_PORT)
    users = db_man.query('SELECT * FROM users;')
    pass

def test3():
    db_man = MariaDbDatabaseManager(database.USER, database.PASSWORD,
                                    database.DATABASE, database.DB_HOST, database.DB_PORT)
    new_id = db_man.insert("INSERT INTO users VALUES(DEFAULT, ?, ?, ?, ?);", ('petru', 'petru', 2, True))
    users = db_man.query('SELECT * FROM users;')
    pass

if __name__ == '__main__':
    test3()
