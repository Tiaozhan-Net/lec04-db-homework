-- 参考解：第 2 部分 Q2 姓名不干净
-- NULL、全空格、前后有空格，三种都算。
SELECT id, name, CHAR_LENGTH(name) AS len
FROM members
WHERE name IS NULL
   OR TRIM(name) = ''
   OR name <> TRIM(name)
ORDER BY id ASC;
