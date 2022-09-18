DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS plan;
DROP TABLE IF EXISTS plan_details;
DROP TABLE IF EXISTS questions;
-- DROP TABLE IF EXISTS exam;
-- DROP TABLE IF EXISTS exam_details;

CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  configured boolean DEFAULT 0 
);

CREATE TABLE IF NOT EXISTS plan (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  exam TEXT NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL
);

CREATE TABLE IF NOT EXISTS plan_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plan_id INTEGER,
  week_number INTEGER,
  subject_name TEXT,
  topic_name TEXT,
  required_hours INTEGER,
  completed boolean
);

CREATE TABLE IF NOT EXISTS exam (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exam_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_id INTEGER,
  topic_name TEXT,
  subject_name TEXT,
  required_hours INTEGER
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  topic_id INTEGER,
  question_statement TEXT,
  a TEXT,
  b TEXT,
  c TEXT,
  d TEXT,
  answer CHAR
);

CREATE TABLE IF NOT EXISTS test (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_time TEXT,
  end_time TEXT,
  number_of_questions INTEGER,
  marks INTEGER,
  is_submitted boolean DEFAULT 0
);

CREATE TABLE IF NOT EXISTS test_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  test_id INTEGER,
  question_id INTEGER,
  answer CHAR
);

-- INSERT INTO exam (exam_name) VALUES("gate computer science")
