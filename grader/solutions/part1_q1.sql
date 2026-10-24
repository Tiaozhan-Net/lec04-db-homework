-- 参考解：第 1 部分 Q1
-- 分数 >= 85，按分数降序、学号升序，取前 5 条。输出列名必须是 name, score。
SELECT name, score
FROM members
WHERE score >= 85
ORDER BY score DESC, student_id ASC
LIMIT 5;
