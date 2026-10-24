-- 参考解：第 5 部分 05a —— 加列 + 把"取消报名"改成软删除
-- 指定取消报名的是学号 20230002。

ALTER TABLE members
  ADD COLUMN deleted_at DATETIME(3) NULL AFTER joined_at;

UPDATE members
SET deleted_at = NOW(3)
WHERE student_id = '20230002';
