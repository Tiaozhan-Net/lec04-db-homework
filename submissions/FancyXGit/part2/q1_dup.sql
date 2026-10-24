-- 参考解：第 2 部分 Q1 重复学号
-- 空学号（NULL / 空串 / 全空格）不算重复，先排除。
SELECT student_id, COUNT(*) AS cnt
FROM members
WHERE student_id IS NOT NULL
  AND TRIM(student_id) <> ''
GROUP BY student_id
HAVING COUNT(*) > 1
ORDER BY cnt DESC, student_id ASC;
