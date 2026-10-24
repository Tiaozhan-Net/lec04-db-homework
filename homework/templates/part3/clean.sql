-- 第 3 部分 / 清洗脚本
-- 数据：hw_legacy（28 行）
-- 只改数据；不许 DROP/TRUNCATE、不许重建表、不许写 USE
-- 洗完 14 行
--
-- 要处理的：学号空/非 8 位/前后空格、学号重复、姓名空/前后空格、
--           班级三种写法、专业同义词、分数 NULL/越界、日期三种格式
--
-- 把你的清洗 SQL 写在 START TRANSACTION; 和 COMMIT; 之间。

START TRANSACTION;

-- 在这里写清洗 SQL（UPDATE / DELETE）

-- 确认没问题后提交；想放弃就把 COMMIT 改成 ROLLBACK
COMMIT;

