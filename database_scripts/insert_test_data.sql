USE licenta;

INSERT INTO user_type VALUES(DEFAULT, 'admin');
INSERT INTO user_type VALUES(DEFAULT, 'microservice');
INSERT INTO user_type VALUES(DEFAULT, 'user');

-- Bcrypt hashed passwords
-- password = admin
INSERT INTO user VALUES(DEFAULT, 'admin', '$2a$12$H8gj9A6bWAzrtaxvx2a6tuDsIE69cV4qX4I/K7jIjoZRM0tdCIIim', 1, TRUE);

-- password = microservice
INSERT INTO user VALUES(DEFAULT, 'microservice', '$2a$12$XQ2093DlI9OOAHjS2Rh.OOvkEb/ToguaFkubHPBiqPH/JprQxzy3C', 2, TRUE);

-- password = password
SET @password = '$2a$12$m1iZTjdGI.5fUjBjxOp41.6i0tyB7V19yrRwzdRvmV5y0zkapMjkC';
INSERT INTO user VALUES(DEFAULT, 'crawler_user_1', @password, 3, TRUE);
INSERT INTO user VALUES(DEFAULT, 'crawler_user_2', @password, 3, TRUE);
INSERT INTO user VALUES(DEFAULT, 'genre_computation_user_1', @password, 3, TRUE);
INSERT INTO user VALUES(DEFAULT, 'genre_computation_user_2', @password, 3, TRUE);
INSERT INTO user VALUES(DEFAULT, 'disabled_user', @password, 3, FALSE);

INSERT INTO service VALUES(DEFAULT, 'genre_computation', 50.0);
INSERT INTO service VALUES(DEFAULT, 'crawled_resource', 2.0);

-- user_id, service_id, quantity
INSERT INTO user_to_service VALUES(1, 1, 0);
INSERT INTO user_to_service VALUES(1, 2, 0);

INSERT INTO user_to_service VALUES(2, 1, 0);
INSERT INTO user_to_service VALUES(2, 2, 0);

INSERT INTO user_to_service VALUES(3, 1, 0);
INSERT INTO user_to_service VALUES(3, 2, 0);

INSERT INTO user_to_service VALUES(4, 1, 0);
INSERT INTO user_to_service VALUES(4, 2, 0);

INSERT INTO user_to_service VALUES(5, 1, 0);
INSERT INTO user_to_service VALUES(5, 2, 0);

INSERT INTO user_to_service VALUES(6, 1, 0);
INSERT INTO user_to_service VALUES(6, 2, 0);

INSERT INTO user_to_service VALUES(7, 1, 0);
INSERT INTO user_to_service VALUES(7, 2, 0);

-- 2022 Bills
INSERT INTO bill VALUES(NULL, 5, 892, '2022-1-28', '2022-2-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 623, '2022-2-28', '2022-3-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 422, '2022-3-28', '2022-4-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 591, '2022-4-28', '2022-5-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 873, '2022-5-28', '2022-6-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 231, '2022-6-28', '2022-7-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 862, '2022-7-28', '2022-8-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 222, '2022-8-28', '2022-9-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 671, '2022-9-28', '2022-10-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 620, '2022-10-28', '2022-11-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 692, '2022-11-28', '2022-12-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 433, '2022-12-28', '2023-1-15', TRUE);

-- 2023 Bills
INSERT INTO bill VALUES(NULL, 5, 524, '2023-1-28', '2023-2-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 700, '2023-2-28', '2023-3-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 411, '2023-3-28', '2023-4-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 620, '2023-4-28', '2023-5-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 630, '2023-5-28', '2023-6-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 322, '2023-6-28', '2023-7-15', TRUE);
INSERT INTO bill VALUES(NULL, 5, 584, '2023-7-28', '2023-8-15', TRUE);

INSERT INTO song_format VALUES(DEFAULT, 'MP3');

INSERT INTO song_genre VALUES(DEFAULT, 'Electronic');
INSERT INTO song_genre VALUES(DEFAULT, 'Pop');
INSERT INTO song_genre VALUES(DEFAULT, 'Rock');
INSERT INTO song_genre VALUES(DEFAULT, 'Hip-Hop');
INSERT INTO song_genre VALUES(DEFAULT, 'Instrumental');
INSERT INTO song_genre VALUES(DEFAULT, 'Folk');
INSERT INTO song_genre VALUES(DEFAULT, 'Computing...'); 

INSERT INTO song VALUES(DEFAULT, 5, 5, 'Acceptance');
INSERT INTO song VALUES(DEFAULT, 5, 1, 'Mineral');

INSERT INTO song_info VALUES(1, 'Evgenia Kostitsyna', 1);
INSERT INTO song_info VALUES(2, 'HRCRX', 1);