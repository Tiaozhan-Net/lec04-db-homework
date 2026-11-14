INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('20239001', 'lin02go', '2024-1', '软件工程', 90, '2025-10-01 09:00:00');

INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES
  ('20239002', '张同学', '2023-1', '计算机科学与技术', 77, '2025-10-02 10:00:00'),
  ('20239003', '李同学', '2023-2', '软件工程', 82, '2025-10-02 11:00:00'),
  ('20239004', '王同学', '2024-1', '数据科学与大数据技术', 68, '2025-10-02 12:00:00');

UPDATE members
SET score = 80
WHERE student_id = '20230003';

DELETE FROM members
WHERE student_id = '20230008';
