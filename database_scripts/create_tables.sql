-- CREATE USER 'crud_user'@'localhost' IDENTIFIED BY 'crud_user_password';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON licenta.* TO 'crud_user'@'localhost' WITH GRANT OPTION;

USE licenta;
CREATE TABLE user_type (
	user_type_id INT auto_increment NULL,
	user_type_name VARCHAR(100) NOT NULL,
	PRIMARY KEY (user_type_id)
);

CREATE TABLE user (
  user_id int(11) NOT NULL AUTO_INCREMENT,
  user_name varchar(100) NOT NULL,
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
	CONSTRAINT song_info_FK FOREIGN KEY (original_format_id) REFERENCES song_format(format_id) ON DELETE SET NULL ON UPDATE SET NULL
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