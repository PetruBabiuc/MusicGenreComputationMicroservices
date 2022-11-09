-- user_id, desired_genre_id, domain, bloom_filter, max_crawled_resources, max_computed_genres, finished
SELECT user_id "user_id", s.service_name "service_name", uts.quantity "quantity" 
	FROM users u 
	JOIN users_to_services uts USING(user_id) 
	JOIN services s USING (service_id)
	WHERE user_id=1;
SELECT * FROM song_urls;
SELECT * FROM resources_urls;
SELECT * FROM crawler_states;
SELECT COUNT(*) FROM resources_urls;
SELECT COUNT(DISTINCT(resource_url)) FROM resources_urls;
SELECT s.song_name, g.song_genre_name FROM songs s JOIN song_genres g ON(s.genre_id=g.song_genre_id);