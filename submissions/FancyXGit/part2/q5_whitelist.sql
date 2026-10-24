-- 参考解：第 2 部分 Q5 专业或班级不在白名单
SELECT id, major, class_name
FROM members
WHERE major IS NULL
   OR major NOT IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术')
   OR class_name IS NULL
   OR class_name NOT REGEXP '^[0-9]{4}-[1-9]$'
ORDER BY id ASC;
