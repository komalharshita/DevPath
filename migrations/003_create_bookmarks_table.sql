-- Migration: Create bookmarks table for authenticated users
-- Stores bookmarks for paths, topics, and resources

CREATE TABLE IF NOT EXISTS bookmarks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  resource_type TEXT NOT NULL,
  resource_id INTEGER NOT NULL,
  resource_name TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, resource_type, resource_id)
);

-- Create indexes for efficient queries
CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);
CREATE INDEX idx_bookmarks_resource_type ON bookmarks(resource_type);
CREATE INDEX idx_bookmarks_created_at ON bookmarks(created_at DESC);
CREATE INDEX idx_bookmarks_composite ON bookmarks(user_id, resource_type);
