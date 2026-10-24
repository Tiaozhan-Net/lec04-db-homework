-- 规范版 members：第 1 部分使用（14 行，有完整约束）
-- 本地加载：
--   mysql -u root -p -e "source db/00_clean.sql" hw_clean
-- 说明：这个文件只负责建表 + 灌数据，库要先自己建好（见 docs/00-环境搭建.md）。

DROP TABLE IF EXISTS members;

CREATE TABLE members (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  student_id  CHAR(8)         NOT NULL COMMENT '学号，8 位数字',
  name        VARCHAR(32)     NOT NULL COMMENT '姓名',
  class_name  VARCHAR(8)      NOT NULL COMMENT '班级，形如 2023-1',
  major       VARCHAR(32)     NOT NULL COMMENT '专业',
  score       DECIMAL(5,2)    NOT NULL COMMENT '分数，0-100',
  joined_at   DATETIME(3)     NOT NULL COMMENT '报名时间',
  PRIMARY KEY (id),
  UNIQUE KEY uk_student_id (student_id),
  CONSTRAINT chk_members_name  CHECK (CHAR_LENGTH(TRIM(name)) > 0),
  CONSTRAINT chk_members_score CHECK (score BETWEEN 0 AND 100),
  CONSTRAINT chk_members_sid   CHECK (student_id REGEXP '^[0-9]{8}$'),
  CONSTRAINT chk_members_class CHECK (class_name REGEXP '^[0-9]{4}-[1-9]$'),
  CONSTRAINT chk_members_major CHECK (major IN ('计算机科学与技术', '软件工程', '数据科学与大数据技术'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO members (id, student_id, name, class_name, major, score, joined_at) VALUES
( 1, '20230001', '张三',   '2023-1', '计算机科学与技术',   92.00, '2025-09-01 08:30:00.000'),
( 2, '20230002', '李四',   '2023-1', '软件工程',           85.50, '2025-09-01 09:00:00.000'),
( 3, '20230003', '王五',   '2023-2', '数据科学与大数据技术', 78.00, '2025-09-02 10:15:00.000'),
( 4, '20230004', '赵六',   '2023-2', '计算机科学与技术',   92.00, '2025-09-02 11:20:00.000'),
( 5, '20230005', '钱七',   '2024-1', '软件工程',           88.00, '2025-09-03 08:45:00.000'),
( 6, '20230006', '孙八',   '2024-1', '计算机科学与技术',   76.50, '2025-09-03 13:10:00.000'),
( 7, '20230007', '周九',   '2023-1', '数据科学与大数据技术', 95.00, '2025-09-04 09:30:00.000'),
( 8, '20230008', '吴十',   '2023-2', '软件工程',           81.00, '2025-09-04 14:00:00.000'),
( 9, '20230009', '张九',   '2024-1', '计算机科学与技术',   69.00, '2025-09-05 10:05:00.000'),
(10, '20230010', '冯十二', '2023-1', '软件工程',           88.00, '2025-09-05 15:40:00.000'),
(11, '20230011', '陈十三', '2023-2', '数据科学与大数据技术', 73.50, '2025-09-06 09:20:00.000'),
(12, '20230012', '褚十四', '2024-1', '计算机科学与技术',   84.00, '2025-09-06 16:30:00.000'),
(13, '20230013', '卫十五', '2023-1', '软件工程',           90.00, '2025-09-07 08:00:00.000'),
(14, '20230014', '蒋十六', '2023-2', '计算机科学与技术',   64.00, '2025-09-07 11:50:00.000');
