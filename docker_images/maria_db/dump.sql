CREATE DATABASE licenta;

CREATE USER 'crud_user'@'%' IDENTIFIED BY 'crud_user_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON licenta.* TO 'crud_user'@'%' WITH GRANT OPTION;

FLUSH PRIVILEGES;

-- CREATE

USE licenta;
CREATE TABLE user_type (
	user_type_id INT auto_increment NULL,
	user_type_name VARCHAR(100) NOT NULL,
	PRIMARY KEY (user_type_id)
);

CREATE TABLE user (
  user_id int(11) NOT NULL AUTO_INCREMENT,
  user_name varchar(100) NOT NULL UNIQUE,
  password varchar(100) NOT NULL,
  user_type_id int(11) NOT NULL,
  is_active tinyint(1) NOT NULL,
  PRIMARY KEY (user_id),
  CONSTRAINT user_FK FOREIGN KEY (user_type_id) REFERENCES user_type(user_type_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE song_genre (
	song_genre_id INT auto_increment NULL,
	song_genre_name varchar(100) NOT NULL,
	PRIMARY KEY (song_genre_id)
);

CREATE TABLE song_format (
	format_id INT auto_increment NULL,
	format_name varchar(100) NOT NULL,
	PRIMARY KEY (format_id)
);

CREATE TABLE song (
	song_id INT auto_increment NULL,
	user_id INT NOT NULL,
	genre_id INT NOT NULL,
	song_name varchar(100) NOT NULL,
	PRIMARY KEY (song_id),
	CONSTRAINT song_user_id_FK FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT song_genre_FK FOREIGN KEY (genre_id) REFERENCES song_genre(song_genre_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE song_info (
	song_id INT NOT NULL,
	author varchar(100) NULL,
	original_format_id INT NULL,
	PRIMARY KEY (song_id),
	CONSTRAINT song_info_FK FOREIGN KEY (original_format_id) REFERENCES song_format(format_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE service (
	service_id INT auto_increment NULL,
	service_name VARCHAR(100) NOT NULL,
	price FLOAT NOT NULL,
	PRIMARY KEY (service_id),
	CONSTRAINT service_UN UNIQUE KEY (service_name)
);

CREATE TABLE user_to_service (
	user_id INT NOT NULL,
	service_id INT NOT NULL,
	quantity FLOAT DEFAULT 0 NOT NULL,
	PRIMARY KEY (user_id,service_id),
	CONSTRAINT user_to_service_user_id_FK FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT user_to_service_service_id_FK FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE bill (
	bill_id INT auto_increment NULL,
	user_id INT NOT NULL,
	price FLOAT NOT NULL,
	issue_date DATE NOT NULL,
	deadline DATE NOT NULL,
	is_paid BOOL DEFAULT FALSE NOT NULL,
	PRIMARY KEY (bill_id),
	CONSTRAINT bill_user_id_FK FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE crawler_state (
  user_id int(11) NOT NULL,
  desired_genre_id int(11) NOT NULL,
  domain varchar(100) NOT NULL,
  max_crawled_resources int(11) DEFAULT NULL,
  max_computed_genres int(11) NOT NULL DEFAULT 0,
--   finished tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id),
  CONSTRAINT crawler_state_desired_genre_id_FK FOREIGN KEY (desired_genre_id) REFERENCES song_genre(song_genre_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT crawler_state_user_id_FK FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE resource_url (
	resource_url_id INT auto_increment NULL,
	resource_url varchar(100) NOT NULL,
	user_id INT NOT NULL,
	PRIMARY KEY (resource_url_id),
	CONSTRAINT resource_url_FK FOREIGN KEY (user_id) REFERENCES crawler_state(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE bloom_filter (
	user_id INT NOT NULL,
	value LONGTEXT DEFAULT NULL NULL,
	UNIQUE KEY bloom_filter_UN (user_id),
	CONSTRAINT bloom_filter_FK FOREIGN KEY (user_id) REFERENCES crawler_state(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE song_url (
	song_url_id INT auto_increment NULL,
	song_url varchar(100) NOT NULL,
	user_id INT NOT NULL,
	genre_id INT NOT NULL,
	PRIMARY KEY (song_url_id),
	CONSTRAINT song_url_FK_user_id_FK FOREIGN KEY (user_id) REFERENCES crawler_state(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT song_url_song_genre_id_FK FOREIGN KEY (genre_id) REFERENCES song_genre(song_genre_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- INSERT
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