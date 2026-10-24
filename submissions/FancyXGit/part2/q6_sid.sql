-- 参考解：第 2 部分 Q6 学号不是 8 位数字
-- 先 TRIM 再判断：前后有空格但里面是 8 位数字的，不算问题。
SELECT id, student_id
FROM members
WHERE student_id IS NULL
   OR TRIM(student_id) NOT REGEXP '^[0-9]{8}$'
ORDER BY id ASC;
