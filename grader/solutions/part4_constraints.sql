-- 参考解：第 4 部分加约束
-- 唯一索引名用 uk_student_id，第 5 部分会按这个名字把它迁成"活跃才唯一"。

ALTER TABLE members
  MODIFY student_id VARCHAR(32)  NOT NULL,
  MODIFY name       VARCHAR(32)  NOT NULL,
  MODIFY class_name VARCHAR(16)  NOT NULL,
  MODIFY major      VARCHAR(32)  NOT NULL,
  MODIFY score      DECIMAL(5,2) NOT NULL,
  MODIFY joined_at  DATETIME(3)  NOT NULL;

ALTER TABLE members
  ADD UNIQUE KEY uk_student_id (student_id);

ALTER TABLE members
  ADD CONSTRAINT chk_members_name  CHECK (CHAR_LENGTH(TRIM(name)) > 0),
  ADD CONSTRAINT chk_members_score CHECK (score BETWEEN 0 AND 100),
  ADD CONSTRAINT chk_members_sid   CHECK (student_id REGEXP '^[0-9]{8}$'),
  ADD CONSTRAINT chk_members_major CHECK (major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')),
  ADD CONSTRAINT chk_members_class CHECK (class_name REGEXP '^[0-9]{4}-[1-9]$');
