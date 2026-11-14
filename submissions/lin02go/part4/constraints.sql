ALTER TABLE members
  MODIFY COLUMN student_id VARCHAR(32) NOT NULL,
  MODIFY COLUMN name VARCHAR(32) NOT NULL,
  MODIFY COLUMN class_name VARCHAR(16) NOT NULL,
  MODIFY COLUMN major VARCHAR(32) NOT NULL,
  MODIFY COLUMN score DECIMAL(5,2) NOT NULL,
  MODIFY COLUMN joined_at DATETIME(3) NOT NULL,
  ADD UNIQUE KEY uk_student_id (student_id),
  ADD CONSTRAINT chk_members_name CHECK (CHAR_LENGTH(TRIM(name)) > 0),
  ADD CONSTRAINT chk_members_score CHECK (score BETWEEN 0 AND 100),
  ADD CONSTRAINT chk_members_sid CHECK (student_id REGEXP '^[0-9]{8}$'),
  ADD CONSTRAINT chk_members_major CHECK (
      major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')
  ),
  ADD CONSTRAINT chk_members_class CHECK (class_name REGEXP '^[0-9]{4}-[1-9]$');
