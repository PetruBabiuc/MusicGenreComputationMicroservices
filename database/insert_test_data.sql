USE licenta;

INSERT INTO user_types VALUES(DEFAULT, 'user');
INSERT INTO user_types VALUES(DEFAULT, 'admin');

INSERT INTO users VALUES(DEFAULT, 'crawler_user_1', 'password', 1, TRUE);
INSERT INTO users VALUES(DEFAULT, 'crawler_user_2', 'password', 1, TRUE);
INSERT INTO users VALUES(DEFAULT, 'genre_computation_user_1', 'password', 1, TRUE);
INSERT INTO users VALUES(DEFAULT, 'genre_computation_user_2', 'password', 1, TRUE);

INSERT INTO services VALUES(DEFAULT, 'genre_computation', 50.0);
INSERT INTO services VALUES(DEFAULT, 'crawled_resource', 2.0);

-- join_id, user_id, service_id, quantity
INSERT INTO users_to_services VALUES(1, 1, 0);
INSERT INTO users_to_services VALUES(1, 2, 0);

INSERT INTO users_to_services VALUES(2, 1, 0);
INSERT INTO users_to_services VALUES(2, 2, 0);

INSERT INTO users_to_services VALUES(3, 1, 0);
INSERT INTO users_to_services VALUES(3, 2, 0);

INSERT INTO users_to_services VALUES(4, 1, 0);
INSERT INTO users_to_services VALUES(4, 2, 0);

INSERT INTO formats VALUES(DEFAULT, 'MP3');

INSERT INTO song_genres VALUES(DEFAULT, 'Electronic');
INSERT INTO song_genres VALUES(DEFAULT, 'Pop');
INSERT INTO song_genres VALUES(DEFAULT, 'Rock');
INSERT INTO song_genres VALUES(DEFAULT, 'Hip-Hop');
INSERT INTO song_genres VALUES(DEFAULT, 'Instrumental');
INSERT INTO song_genres VALUES(DEFAULT, 'Folk');
INSERT INTO song_genres VALUES(DEFAULT, 'Computing...'); 

INSERT INTO songs VALUES(DEFAULT, 4, 2, 'Umbrella');
INSERT INTO songs VALUES(DEFAULT, 4, 1, 'Memories');

INSERT INTO song_info VALUES(1, 'Rihanna', 1);
INSERT INTO song_info VALUES(2, 'David Guetta', 1);

-- user_id, desired_genre_id, domain, bloom_filter, max_crawled_resources, max_computed_genres, finished
-- INSERT INTO crawler_states VALUES(1, 1, 'https://cdn.freesound.org/', NULL, 1000, 1000, DEFAULT);

SELECT * FROM song_urls su  ;