-- Create the database
CREATE DATABASE IF NOT EXISTS mood_tracker;
USE mood_tracker;

-- Create table for mood entries
CREATE TABLE IF NOT EXISTS mood_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    text_input TEXT,
    voice_input TEXT,
    sentiment_score FLOAT,
    mood_category ENUM('Happy', 'Sad', 'Neutral'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for daily analysis
CREATE TABLE IF NOT EXISTS daily_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    happy_count INT DEFAULT 0,
    sad_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    total_entries INT DEFAULT 0,
    average_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for weekly analysis
CREATE TABLE IF NOT EXISTS weekly_analysis (
    id INT AUTO_INCREMENT PRIMARY KEY,
    week_start_date DATE NOT NULL,
    happy_count INT DEFAULT 0,
    sad_count INT DEFAULT 0,
    neutral_count INT DEFAULT 0,
    total_entries INT DEFAULT 0,
    average_sentiment FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
); 