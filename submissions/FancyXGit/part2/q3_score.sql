-- 参考解：第 2 部分 Q3 分数越界
SELECT id, score
FROM members
WHERE score < 0 OR score > 100
ORDER BY id ASC;
