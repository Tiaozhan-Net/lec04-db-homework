-- 参考解：第 1 部分 Q2
-- 姓张的，输出列 name, student_id，按学号升序。
SELECT name, student_id
FROM members
WHERE name LIKE '张%'
ORDER BY student_id ASC;
