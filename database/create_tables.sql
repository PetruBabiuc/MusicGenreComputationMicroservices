CREATE TABLE licenta.user_types (
	user_type_id INT auto_increment NULL,
	user_type_name VARCHAR(100) NOT NULL,
	CONSTRAINT user_types_PK PRIMARY KEY (user_type_id)
);

CREATE TABLE licenta.users (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` varchar(100) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_type_id` int(11) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  PRIMARY KEY (`user_id`),
  KEY `users_FK` (`user_type_id`),
  CONSTRAINT `users_FK` FOREIGN KEY (`user_type_id`) REFERENCES `user_types` (`user_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.song_genres (
	song_genre_id INT auto_increment NULL,
	song_genre_name varchar(100) NOT NULL,
	CONSTRAINT song_genres_PK PRIMARY KEY (song_genre_id)
);

CREATE TABLE licenta.formats (
	format_id INT auto_increment NULL,
	format_name varchar(100) NOT NULL,
	CONSTRAINT formats_PK PRIMARY KEY (format_id)
);

CREATE TABLE licenta.songs (
	song_id INT auto_increment NULL,
	user_id INT NOT NULL,
	genre_id INT NOT NULL,
	song_name varchar(100) NOT NULL,
	CONSTRAINT songs_PK PRIMARY KEY (song_id),
	CONSTRAINT songs_user_id_FK FOREIGN KEY (user_id) REFERENCES licenta.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT songs_genre_FK FOREIGN KEY (genre_id) REFERENCES licenta.song_genres(song_genre_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.song_info (
	song_id INT NOT NULL,
	author varchar(100) NULL,
	original_format_id INT NULL,
	CONSTRAINT song_info_PK PRIMARY KEY (song_id),
	CONSTRAINT song_info_FK FOREIGN KEY (original_format_id) REFERENCES licenta.formats(format_id) ON DELETE SET NULL ON UPDATE SET NULL
);

CREATE TABLE licenta.services (
	service_id INT auto_increment NULL,
	service_name VARCHAR(100) NOT NULL,
	price FLOAT NOT NULL,
	CONSTRAINT services_PK PRIMARY KEY (service_id),
	CONSTRAINT services_UN UNIQUE KEY (service_name)
);

CREATE TABLE licenta.users_to_services (
	user_id INT NOT NULL,
	service_id INT NOT NULL,
	quantity FLOAT DEFAULT 0 NOT NULL,
	CONSTRAINT users_to_services_PK PRIMARY KEY (user_id,service_id),
	CONSTRAINT users_to_services_user_id_FK FOREIGN KEY (user_id) REFERENCES licenta.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT users_to_services_service_id_FK FOREIGN KEY (service_id) REFERENCES licenta.services(service_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.bills (
	bill_id INT auto_increment NULL,
	user_id INT NOT NULL,
	price FLOAT NOT NULL,
	deadline DATE NOT NULL,
	is_paid BOOL DEFAULT FALSE NOT NULL,
	CONSTRAINT bills_PK PRIMARY KEY (bill_id),
	CONSTRAINT bills_user_id_FK FOREIGN KEY (user_id) REFERENCES licenta.users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.crawler_states (
  `user_id` int(11) NOT NULL,
  `desired_genre_id` int(11) NOT NULL,
  `domain` varchar(100) NOT NULL,
  `bloom_filter` varchar(10000) DEFAULT NULL,
  `max_crawled_resources` int(11) DEFAULT NULL,
  `max_computed_genres` int(11) NOT NULL DEFAULT 0,
  `finished` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `crawler_states_desired_genre_id_FK` FOREIGN KEY (`desired_genre_id`) REFERENCES `song_genres` (`song_genre_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `crawler_states_user_id_FK` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.resources_urls (
	resource_url_id INT auto_increment NULL,
	resource_url varchar(100) NOT NULL,
	user_id INT NOT NULL,
	CONSTRAINT resources_urls_PK PRIMARY KEY (resource_url_id),
	CONSTRAINT resources_urls_FK FOREIGN KEY (user_id) REFERENCES licenta.crawler_states(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE licenta.song_urls (
	song_url_id INT auto_increment NULL,
	song_url varchar(100) NOT NULL,
	user_id INT NOT NULL,
	genre_id INT NOT NULL,
	CONSTRAINT song_urls_PK PRIMARY KEY (song_url_id),
	CONSTRAINT song_urls_FK FOREIGN KEY (user_id) REFERENCES licenta.crawler_states(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT song_urls_FK_1 FOREIGN KEY (genre_id) REFERENCES licenta.song_genres(song_genre_id) ON DELETE CASCADE ON UPDATE CASCADE
);