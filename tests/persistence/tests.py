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


if __name__ == '__main__':
    test1()
