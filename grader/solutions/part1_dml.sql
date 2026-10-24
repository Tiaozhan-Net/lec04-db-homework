-- 参考解：第 1 部分的 4 条 DML
-- 只在本地手动跑，评测里是按任务书上的固定值逐条断言的。
-- 把第一行的名字换成你的 GitHub 用户名。

SET @name = '你的GitHub用户名';

-- 1. 新增一条
INSERT INTO members (student_id, name, class_name, major, score, joined_at)
VALUES ('20239001', @name, '2024-1', '软件工程', 90.00, '2025-10-01 09:00:00');

-- 2. 批量新增三条
INSERT INTO members (student_id, name, class_name, major, score, joined_at) VALUES
('20239002', '张同学', '2023-1', '计算机科学与技术',   77.00, '2025-10-02 10:00:00'),
('20239003', '李同学', '2023-2', '软件工程',           82.00, '2025-10-02 11:00:00'),
('20239004', '王同学', '2024-1', '数据科学与大数据技术', 68.00, '2025-10-02 12:00:00');

-- 3. 把学号 20230003 的分数改成 80
UPDATE members SET score = 80.00 WHERE student_id = '20230003';

-- 4. 删除学号 20230008 的记录
DELETE FROM members WHERE student_id = '20230008';
