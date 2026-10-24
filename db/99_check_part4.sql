-- 第 4 部分自查：看约束和类型到底加上了没有。
--
-- 用法（在仓库根目录）：
--   mysql -u root -p --default-character-set=utf8mb4 -e "source db/99_check_part4.sql"
--
-- 前提：hw_legacy 里已经跑过 part3/clean.sql 和 part4/constraints.sql。
--
-- 输出：7 行，结果列全是 OK 就说明结构齐了。
-- 至于「真的拦得住吗」，跑一遍你自己的 errors.sql，看报错码。

USE hw_legacy;

DROP TEMPORARY TABLE IF EXISTS t_check;
CREATE TEMPORARY TABLE t_check (
  item   VARCHAR(64),
  state  VARCHAR(128),
  result VARCHAR(16)
);

INSERT INTO t_check
SELECT '六列 NOT NULL',
       CONCAT(SUM(IS_NULLABLE = 'NO'), ' / 6 列都是 NOT NULL'),
       IF(SUM(IS_NULLABLE = 'NO') = 6, 'OK', '还差')
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'hw_legacy'
  AND TABLE_NAME = 'members'
  AND COLUMN_NAME IN ('student_id', 'name', 'class_name', 'major', 'score', 'joined_at');

INSERT INTO t_check
SELECT '学号唯一索引',
       CONCAT(COUNT(*), ' 个第一列是 student_id 的唯一索引'),
       IF(COUNT(*) > 0, 'OK', '没有')
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'hw_legacy'
  AND TABLE_NAME = 'members'
  AND NON_UNIQUE = 0
  AND INDEX_NAME <> 'PRIMARY'
  AND SEQ_IN_INDEX = 1
  AND COLUMN_NAME = 'student_id';

INSERT INTO t_check
SELECT 'joined_at 类型',
       COALESCE(
         (SELECT CONCAT(DATA_TYPE, '(', COALESCE(DATETIME_PRECISION, '-'), ')')
          FROM information_schema.COLUMNS
          WHERE TABLE_SCHEMA = 'hw_legacy' AND TABLE_NAME = 'members' AND COLUMN_NAME = 'joined_at'),
         '没有这列'),
       IF(EXISTS(
            SELECT 1 FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'hw_legacy' AND TABLE_NAME = 'members'
              AND COLUMN_NAME = 'joined_at'
              AND DATA_TYPE = 'datetime' AND DATETIME_PRECISION = 3),
          'OK', '不对');

INSERT INTO t_check
SELECT 'score 类型',
       COALESCE(
         (SELECT CONCAT(DATA_TYPE, '(', NUMERIC_PRECISION, ',', NUMERIC_SCALE, ')')
          FROM information_schema.COLUMNS
          WHERE TABLE_SCHEMA = 'hw_legacy' AND TABLE_NAME = 'members' AND COLUMN_NAME = 'score'),
         '没有这列'),
       IF(EXISTS(
            SELECT 1 FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = 'hw_legacy' AND TABLE_NAME = 'members'
              AND COLUMN_NAME = 'score'
              AND DATA_TYPE = 'decimal' AND NUMERIC_PRECISION = 5 AND NUMERIC_SCALE = 2),
          'OK', '不对');

INSERT INTO t_check
SELECT 'CHECK 约束个数',
       CONCAT(COUNT(*), ' 个（题目要 5 个）'),
       IF(COUNT(*) >= 5, 'OK', '不够')
FROM information_schema.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'hw_legacy'
  AND TABLE_NAME = 'members'
  AND CONSTRAINT_TYPE = 'CHECK';

INSERT INTO t_check
SELECT 'CHECK 名字',
       COALESCE(GROUP_CONCAT(CONSTRAINT_NAME ORDER BY CONSTRAINT_NAME SEPARATOR ', '), '一个都没有'),
       IF(COUNT(*) >= 5, 'OK', '不够')
FROM information_schema.TABLE_CONSTRAINTS
WHERE TABLE_SCHEMA = 'hw_legacy'
  AND TABLE_NAME = 'members'
  AND CONSTRAINT_TYPE = 'CHECK';

INSERT INTO t_check
SELECT '唯一索引名字',
       COALESCE(GROUP_CONCAT(DISTINCT INDEX_NAME ORDER BY INDEX_NAME SEPARATOR ', '), '一个都没有'),
       IF(EXISTS(
            SELECT 1 FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = 'hw_legacy' AND TABLE_NAME = 'members'
              AND NON_UNIQUE = 0 AND INDEX_NAME = 'uk_student_id'),
          'OK（第 5 部分要用这个名字）', '建议改名 uk_student_id')
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'hw_legacy'
  AND TABLE_NAME = 'members'
  AND NON_UNIQUE = 0
  AND INDEX_NAME <> 'PRIMARY';

SELECT item AS 检查项, state AS 现状, result AS 结果 FROM t_check;

DROP TEMPORARY TABLE t_check;
