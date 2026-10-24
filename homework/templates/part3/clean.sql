-- 第 3 部分 / 清洗脚本
-- 数据：hw_legacy（28 行）
-- 只能用 UPDATE / DELETE，原地清洗：不许 DROP TABLE、不许 TRUNCATE、不许建新表
-- 洗完 14 行
--
-- 要处理的：学号空/非 8 位/前后空格、学号重复、姓名空/前后空格、
--           班级三种写法、专业同义词、分数 NULL/越界、日期三种格式
--
-- 自查：docker compose run --rm grader python grader/run.py --part 3

