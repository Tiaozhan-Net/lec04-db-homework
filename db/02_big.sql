-- 加分部分用的 20 万行数据（第 5 部分完成后的表结构：有 deleted_at，有函数唯一索引）
-- 本地加载：
--   mysql -u root -p -e "source db/02_big.sql" hw_bonus
-- 大约需要 20-60 秒，只在做加分题时才需要跑。

SET SESSION cte_max_recursion_depth = 300000;

DROP TABLE IF EXISTS members;

CREATE TABLE members (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  student_id  VARCHAR(32)     NOT NULL,
  name        VARCHAR(32)     NOT NULL,
  class_name  VARCHAR(16)     NOT NULL,
  major       VARCHAR(32)     NOT NULL,
  score       DECIMAL(5,2)    NOT NULL,
  joined_at   DATETIME(3)     NOT NULL,
  deleted_at  DATETIME(3)     NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_student_id (student_id, (IF(deleted_at IS NULL, 1, NULL))),
  CONSTRAINT chk_members_name  CHECK (CHAR_LENGTH(TRIM(name)) > 0),
  CONSTRAINT chk_members_score CHECK (score BETWEEN 0 AND 100),
  CONSTRAINT chk_members_sid   CHECK (student_id REGEXP '^[0-9]{8}$'),
  CONSTRAINT chk_members_class CHECK (class_name REGEXP '^[0-9]{4}-[1-9]$'),
  CONSTRAINT chk_members_major CHECK (major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 用 6 个数字位交叉连接造 200000 行，不依赖存储过程。
DROP TABLE IF EXISTS digits;
DROP TABLE IF EXISTS seq;

CREATE TABLE digits (d INT PRIMARY KEY);
INSERT INTO digits VALUES (0),(1),(2),(3),(4),(5),(6),(7),(8),(9);

CREATE TABLE seq (n INT PRIMARY KEY);

INSERT INTO seq (n)
SELECT d0.d + d1.d * 10 + d2.d * 100 + d3.d * 1000 + d4.d * 10000 + f.d * 100000 + 1
FROM digits d0
CROSS JOIN digits d1
CROSS JOIN digits d2
CROSS JOIN digits d3
CROSS JOIN digits d4
CROSS JOIN (SELECT 0 AS d UNION ALL SELECT 1) f;

INSERT INTO members (student_id, name, class_name, major, score, joined_at, deleted_at)
SELECT
  CONCAT('9', LPAD(s.n, 7, '0')),
  IF(s.n % 10 < 2, CONCAT('张', s.n % 200), CONCAT('同学', s.n)),
  CASE s.n % 3 WHEN 0 THEN '2023-1' WHEN 1 THEN '2023-2' ELSE '2024-1' END,
  CASE
    WHEN s.n % 10 < 6 THEN '计算机科学与技术'
    WHEN s.n % 10 < 9 THEN '软件工程'
    ELSE '数据科学与大数据技术'
  END,
  s.n % 101,
  DATE_ADD('2025-01-01 00:00:00', INTERVAL s.n MINUTE),
  NULL
FROM seq s;

DROP TABLE seq;
DROP TABLE digits;

ANALYZE TABLE members;

SELECT COUNT(*) AS rows_loaded FROM members;
