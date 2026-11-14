CREATE INDEX idx_major_score ON members (major, score);
CREATE INDEX idx_class_joined ON members (class_name, joined_at);
CREATE INDEX idx_major_name ON members (major, name);
