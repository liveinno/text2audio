CREATE TABLE users (
	user_id INTEGER NOT NULL, 
	username VARCHAR, 
	first_name VARCHAR, 
	last_name VARCHAR, 
	language_code VARCHAR, 
	is_premium BOOLEAN, 
	created_at DATETIME, 
	updated_at DATETIME, 
	PRIMARY KEY (user_id)
);
CREATE TABLE user_settings (
	user_id INTEGER NOT NULL, 
	tts_engine VARCHAR, 
	voice_type VARCHAR, 
	language VARCHAR, 
	audio_format VARCHAR, 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE TABLE request_counters (
	user_id INTEGER NOT NULL, 
	hourly_count INTEGER, 
	daily_count INTEGER, 
	last_hourly_reset DATETIME, 
	last_daily_reset DATETIME, 
	PRIMARY KEY (user_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
CREATE TABLE tasks (
	task_id VARCHAR NOT NULL, 
	user_id INTEGER, 
	status VARCHAR, 
	text_length INTEGER, 
	file_name VARCHAR, 
	created_at DATETIME, 
	updated_at DATETIME, 
	estimated_time INTEGER, 
	PRIMARY KEY (task_id), 
	FOREIGN KEY(user_id) REFERENCES users (user_id)
);
