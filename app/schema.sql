DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS plan;
DROP TABLE IF EXISTS plan_details;
DROP TABLE IF EXISTS exam;
-- DROP TABLE IF EXISTS exam_details;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  configured boolean DEFAULT 0 
);

CREATE TABLE plan (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  exam TEXT NOT NULL,
  start_date date NOT NULL,
  end_date date NOT NULL
);

CREATE TABLE plan_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  plan_id INTEGER,
  week_number INTEGER,
  subject_name TEXT,
  topic_name TEXT,
  completed boolean
);

CREATE TABLE exam (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_name TEXT NOT NULL
);

CREATE TABLE exam_details (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  exam_id INTEGER,
  topic_name TEXT,
  subject_name TEXT
);
