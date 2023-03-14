-- user_id, desired_genre_id, domain, bloom_filter, max_crawled_resources, max_computed_genres, finished
SELECT user_id "user_id", s.service_name "service_name", uts.quantity "quantity" 
	FROM user u 
	JOIN user_to_service uts USING(user_id) 
	JOIN service s USING (service_id)
	WHERE user_id=7
;

SELECT * FROM song_url;

SELECT * FROM song;

SELECT * FROM user_type;

SELECT * FROM resource_url;

SELECT * FROM crawler_state;

SELECT * FROM bill;

SELECT * FROM song_genre;

SELECT COUNT(*) FROM resource_url;

SELECT COUNT(DISTINCT(r.resource_url)) FROM resource_url r;

SELECT s.song_name, g.song_genre_name 
	FROM song s 
	JOIN song_genre g ON(s.genre_id=g.song_genre_id);
	
SELECT * FROM bloom_filter;