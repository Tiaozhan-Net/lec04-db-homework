-- 在同一条 ALTER TABLE 中替换索引，避免出现无唯一约束的窗口。
ALTER TABLE members
  DROP INDEX uk_student_id,
  ADD UNIQUE KEY uk_student_id (student_id, (IF(deleted_at IS NULL, 1, NULL)));
