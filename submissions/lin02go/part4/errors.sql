-- @error 1062
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
SELECT student_id, '重复测试', class_name, major, score, joined_at
FROM members
ORDER BY id
LIMIT 1;

-- @error 1048
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('99900002', NULL, '2023-1', '软件工程', 60, '2025-12-01 00:00:00');

-- @error 1364
INSERT INTO members (student_id, class_name, major, score, joined_at)
VALUES ('99900003', '2023-1', '软件工程', 60, '2025-12-01 00:00:00');

-- @error 3819
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('99900004', '分数测试', '2023-1', '软件工程', 101, '2025-12-01 00:00:00');
