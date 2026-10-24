-- 参考解：第 4 部分四条必错语句
-- 每条语句只留一处错误，其余字段都是合法值。

-- @error 1062
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
SELECT student_id, '测试甲', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00'
FROM members LIMIT 1;

-- @error 1048
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('99900002', NULL, '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00');

-- @error 1364
INSERT INTO members (student_id, class_name, major, score, joined_at)
VALUES ('99900003', '2023-1', '软件工程', 60.00, '2025-12-01 00:00:00');

-- @error 3819
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('99900004', '测试丁', '2023-1', '软件工程', 101.00, '2025-12-01 00:00:00');
