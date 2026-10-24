-- 第 3 部分自查：把你本地的 hw_legacy 和「参考解洗出来的表」逐列对比。
--
-- 用法（在仓库根目录，用命令行，不要用 Workbench）：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_check_part3.sql"
--
-- 前提：
--   1. hw_legacy 存在，而且 db/01_legacy.sql 灌过；
--   2. 你已经把 part3/clean.sql 在 hw_legacy 上跑过了。
--
-- 输出：
--   第一张表看结论，第二张表是明细。明细为空就是全对。

DROP DATABASE IF EXISTS hw_check;
CREATE DATABASE hw_check CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

USE hw_check;
SOURCE db/01_legacy.sql;
SOURCE grader/solutions/part3_clean.sql;

USE hw_legacy;

DROP TEMPORARY TABLE IF EXISTS t_diff;

CREATE TEMPORARY TABLE t_diff AS
SELECT '只在你的表里' AS problem, a.student_id, a.name, a.class_name, a.major, a.score, a.joined_at
FROM hw_legacy.members AS a
LEFT JOIN hw_check.members AS b ON b.student_id = TRIM(a.student_id)
WHERE b.student_id IS NULL
UNION ALL
SELECT '只在参考答案里', b.student_id, b.name, b.class_name, b.major, b.score, b.joined_at
FROM hw_check.members AS b
LEFT JOIN hw_legacy.members AS a ON TRIM(a.student_id) = b.student_id
WHERE a.student_id IS NULL
UNION ALL
SELECT '字段不一样', a.student_id, a.name, a.class_name, a.major, a.score, a.joined_at
FROM hw_legacy.members AS a
JOIN hw_check.members AS b ON b.student_id = TRIM(a.student_id)
WHERE NOT (
      a.student_id  <=> b.student_id
  AND a.name        <=> b.name
  AND a.class_name  <=> b.class_name
  AND a.major       <=> b.major
  AND a.score       <=> b.score
  AND a.joined_at   <=> b.joined_at
);

SELECT
  (SELECT COUNT(*) FROM hw_legacy.members) AS 你的行数,
  (SELECT COUNT(*) FROM hw_check.members)  AS 参考答案行数,
  (SELECT COUNT(*) FROM t_diff)            AS 明细条数,
  CASE
    WHEN (SELECT COUNT(*) FROM hw_legacy.members) <> (SELECT COUNT(*) FROM hw_check.members)
      THEN '行数就不对，先看行数'
    WHEN (SELECT COUNT(*) FROM t_diff) = 0
      THEN '全对'
    ELSE '有差异，看下面明细'
  END AS 结论;

SELECT * FROM t_diff;
