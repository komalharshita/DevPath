-- Migration: Create certificates table for tracking completed path certificates
-- This table stores certificate records with verification codes

CREATE TABLE IF NOT EXISTS certificates (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  path_id INTEGER NOT NULL,
  verification_code TEXT UNIQUE NOT NULL,
  completion_date TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (path_id) REFERENCES paths(id) ON DELETE CASCADE,
  UNIQUE(user_id, path_id)
);

-- Create index for fast verification code lookups
CREATE INDEX idx_certificates_verification_code ON certificates(verification_code);

-- Create index for user certificate retrieval
CREATE INDEX idx_certificates_user_id ON certificates(user_id);

-- Create index for path certificate retrieval
CREATE INDEX idx_certificates_path_id ON certificates(path_id);
