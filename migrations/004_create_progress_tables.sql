-- Migration: Create progress tracking tables
-- Tracks user progress on topics and paths

CREATE TABLE IF NOT EXISTS user_topic_progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  completed INTEGER DEFAULT 0,
  completed_at TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, topic_id)
);

CREATE TABLE IF NOT EXISTS user_activity (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  topic_id INTEGER NOT NULL,
  date DATE NOT NULL,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, topic_id, date)
);

-- Create indexes for efficient queries
CREATE INDEX idx_progress_user_id ON user_topic_progress(user_id);
CREATE INDEX idx_progress_completed ON user_topic_progress(completed);
CREATE INDEX idx_activity_user_id ON user_activity(user_id);
CREATE INDEX idx_activity_date ON user_activity(date);
