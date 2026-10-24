-- 参考解：加分 B1
-- 要让函数键那一段也参与定位，WHERE 里的表达式必须和 05b 建的索引表达式一模一样。
SELECT id, name
FROM members
WHERE student_id = '90000001'
  AND (IF(deleted_at IS NULL, 1, NULL)) = 1;
