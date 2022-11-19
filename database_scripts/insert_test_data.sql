USE licenta;

INSERT INTO user_type VALUES(DEFAULT, 'user');
INSERT INTO user_type VALUES(DEFAULT, 'admin');

INSERT INTO user VALUES(DEFAULT, 'crawler_user_1', 'password', 1, TRUE);
INSERT INTO user VALUES(DEFAULT, 'crawler_user_2', 'password', 1, TRUE);
INSERT INTO user VALUES(DEFAULT, 'genre_computation_user_1', 'password', 1, TRUE);
INSERT INTO user VALUES(DEFAULT, 'genre_computation_user_2', 'password', 1, TRUE);

INSERT INTO service VALUES(DEFAULT, 'genre_computation', 50.0);
INSERT INTO service VALUES(DEFAULT, 'crawled_resource', 2.0);

-- join_id, user_id, service_id, quantity
INSERT INTO user_to_service VALUES(1, 1, 0);
INSERT INTO user_to_service VALUES(1, 2, 0);

INSERT INTO user_to_service VALUES(2, 1, 0);
INSERT INTO user_to_service VALUES(2, 2, 0);

INSERT INTO user_to_service VALUES(3, 1, 0);
INSERT INTO user_to_service VALUES(3, 2, 0);

INSERT INTO user_to_service VALUES(4, 1, 0);
INSERT INTO user_to_service VALUES(4, 2, 0);

INSERT INTO song_format VALUES(DEFAULT, 'MP3');

INSERT INTO song_genre VALUES(DEFAULT, 'Electronic');
INSERT INTO song_genre VALUES(DEFAULT, 'Pop');
INSERT INTO song_genre VALUES(DEFAULT, 'Rock');
INSERT INTO song_genre VALUES(DEFAULT, 'Hip-Hop');
INSERT INTO song_genre VALUES(DEFAULT, 'Instrumental');
INSERT INTO song_genre VALUES(DEFAULT, 'Folk');
INSERT INTO song_genre VALUES(DEFAULT, 'Computing...'); 

INSERT INTO song VALUES(DEFAULT, 4, 2, 'Umbrella');
INSERT INTO song VALUES(DEFAULT, 4, 1, 'Memories');

INSERT INTO song_info VALUES(1, 'Rihanna', 1);
INSERT INTO song_info VALUES(2, 'David Guetta', 1);

INSERT INTO crawler_state VALUES(1, 1, 'http://google.com/', 99, 88, FALSE);
INSERT INTO bloom_filter VALUES(1, 'BIG BASE64 STRING');