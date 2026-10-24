-- 参考解：第 1 部分 Q3
-- 分数最高的 3 位，输出列 name, score，并列时学号小的在前。
SELECT name, score
FROM members
ORDER BY score DESC, student_id ASC
LIMIT 3;
