-- 参考解：加分 B2
-- 三条索引，正好覆盖四类查询，第一条查询用现成的 uk_student_id。

CREATE INDEX idx_major_score  ON members (major, score);
CREATE INDEX idx_class_joined ON members (class_name, joined_at);
CREATE INDEX idx_major_name   ON members (major, name);
