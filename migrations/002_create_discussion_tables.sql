-- Migration: Create discussion threads and comments tables
-- Enables community discussion for learning paths

CREATE TABLE IF NOT EXISTS discussion_threads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  FOREIGN KEY (path_id) REFERENCES paths(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS thread_comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  thread_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (thread_id) REFERENCES discussion_threads(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for efficient queries
CREATE INDEX idx_threads_path_id ON discussion_threads(path_id);
CREATE INDEX idx_threads_user_id ON discussion_threads(user_id);
CREATE INDEX idx_threads_updated_at ON discussion_threads(updated_at DESC);
CREATE INDEX idx_comments_thread_id ON thread_comments(thread_id);
CREATE INDEX idx_comments_user_id ON thread_comments(user_id);
