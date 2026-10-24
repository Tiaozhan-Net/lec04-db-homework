-- 参考解：第 1 部分 Q5
-- 每个专业的人数，输出列 major, cnt，按人数降序、专业升序。
SELECT major, COUNT(*) AS cnt
FROM members
GROUP BY major
ORDER BY cnt DESC, major ASC;
