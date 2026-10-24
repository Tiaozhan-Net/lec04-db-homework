-- 参考解：第 5 部分 05b —— 把"学号唯一"迁成"活跃行才唯一"
-- 关键：软删除的行在函数键上是 NULL，唯一索引允许多个 NULL。

ALTER TABLE members
  DROP INDEX uk_student_id;

ALTER TABLE members
  ADD UNIQUE KEY uk_student_id (student_id, (IF(deleted_at IS NULL, 1, NULL)));
