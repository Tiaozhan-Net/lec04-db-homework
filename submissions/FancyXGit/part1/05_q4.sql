-- 参考解：第 1 部分 Q4
-- 计算机科学与技术专业的人数，输出列名必须是 cnt。
SELECT COUNT(*) AS cnt
FROM members
WHERE major = '计算机科学与技术';
