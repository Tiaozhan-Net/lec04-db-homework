-- 加分 B1 / 一条 SELECT
-- 数据：hw_bonus
-- 只查 id, name
-- WHERE 里同时有 student_id 等值条件 + 第 5 部分 05b 里的函数键表达式
-- 判分看 EXPLAIN：used_key_parts 必须是 2
-- 自查：docker compose run --rm grader python grader/run.py --part bonus

