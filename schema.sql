-- Drop and create the database with correct character set
DROP DATABASE IF EXISTS kannada_db;
CREATE DATABASE IF NOT EXISTS kannada_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE kannada_db;

-- 1. Table for Idioms (Matches app.py Idiom model)
-- Columns are now 'explanation_english' and 'explanation_kannada'
CREATE TABLE idioms (
    idiom VARCHAR(255) PRIMARY KEY,
    explanation_english TEXT NOT NULL,
    explanation_kannada TEXT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Table for History (Matches app.py History model)
-- Added the 'email' column
CREATE TABLE history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255),
    original_sentence TEXT,
    status VARCHAR(50),
    match_type VARCHAR(50),
    idiom VARCHAR(255),
    confidence INT,
    translation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. Table for Suggestions (Matches app.py Suggestion model)
-- Columns are now 'explanation_english' and 'explanation_kannada'
CREATE TABLE suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idiom VARCHAR(255) NOT NULL,
    
    explanation_kannada TEXT NOT NULL,
   
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    
-- 4. Load your existing Idiom data
-- This command now maps the TSV columns to 'idiom' and 'explanation_english'.
LOAD DATA INFILE 'files/location'
INTO TABLE idioms
CHARACTER SET 'utf8mb4'
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(idiom, explanation_kannada); -- Maps 2nd TSV column to 'explanation_english'

CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- SELECT * FROM idioms LIMIT 10;


